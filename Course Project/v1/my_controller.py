from ryu.base import app_manager
from ryu.lib import hub
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser
from ryu.controller import dpset
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import arp
import networkx as nx
import time
#importing ether_types
from ryu.lib.packet import ether_types

class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        self.dpset = dpset.DPSet()
        self.graph = nx.Graph()
        self.hosts = {}
        self.paths = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.dpset.add(datapath)

        match = parser.OFPMatch(eth_type=ether.ETH_TYPE_IP,
                                ip_proto=inet.IPPROTO_ICMP)
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 1, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        if eth_pkt.ethertype == ether.ETH_TYPE_ARP:
            arp_pkt = pkt.get_protocol(arp.arp)
            src_ip = arp_pkt.src_ip
            src_mac = eth_pkt.src
            dst_ip = arp_pkt.dst_ip
            dst_mac = eth_pkt.dst

            if src_mac not in self.hosts:
                self.hosts[src_mac] = datapath.id
                self.graph.add_node(src_mac)

            if dst_mac not in self.hosts:
                self.hosts[dst_mac] = datapath.id
                self.graph.add_node(dst_mac)

            self.graph.add_edge(src_mac, dst_mac, weight= self.get_link_cost(src_mac, dst_mac, time.time()))
            if nx.has_path(self.graph, src_mac, dst_mac):
                path = nx.shortest_path(self.graph, src_mac, dst_mac,
                                        weight='weight')
                self.paths[(src_mac, dst_mac)] = path
                self.logger.info("Shortest path from %s to %s: %s",
                                src_mac, dst_mac, path)

            out_port = self.get_out_port(datapath, dst_mac)

            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port,
                                    eth_dst=dst_mac,
                                    eth_src=src_mac)
            self.add_flow(datapath, 2, match, actions)
            self.send_packet(datapath, actions, pkt, in_port)

    def get_out_port(self, datapath, dst_mac):
        src_mac = self.hosts[datapath.id]
        if (src_mac, dst_mac) in self.paths:
            path = self.paths[(src_mac, dst_mac)]
            if len(path) > 2:
                next_hop = path[path.index(src_mac) + 1]
                return self.get_switch_port(datapath.id, next_hop)
            else:
                return self.get_switch_port(datapath.id, dst_mac)
        else:
            return ofproto_v1_3.OFPP_FLOOD

    def get_switch_port(self, switch_id, host_mac):
        switch_dp = self.dpset.get(switch_id)
        parser = switch_dp.ofproto_parser

        for port in switch_dp.ports.values():
            port_no = port.port_no
            match = parser.OFPMatch(eth_dst=host_mac)
            actions = [parser.OFPActionOutput(port_no)]
            out = parser.OFPPacketOut(datapath=switch_dp, buffer_id=0,
                                    in_port=ofproto_v1_3.OFPP_CONTROLLER,
                                    actions=actions,
                                    data=None)
            switch_dp.send_msg(out)
            time.sleep(0.1)

            if host_mac in self.hosts:
                return port_no

        return ofproto_v1_3.OFPP_FLOOD

    def get_link_cost(self, src_mac, dst_mac, start_time):
        switch_src = self.hosts[src_mac]
        switch_dst = self.hosts[dst_mac]
        path = nx.shortest_path(self.graph, switch_src, switch_dst)
        link_cost = 0
        for i in range(len(path) - 1):
            switch1 = path[i]
            switch2 = path[i + 1]
            link_cost += self.graph[switch1][switch2]['weight']

        end_time = time.time()
        return link_cost / (end_time - start_time)

    def send_packet(self, datapath, actions, pkt, in_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        data = pkt.data
        out = parser.OFPPacketOut(datapath=datapath,
                                buffer_id=ofproto.OFP_NO_BUFFER,
                                in_port=in_port,
                                actions=actions,
                                data=data)
        datapath.send_msg(out)

    def compute_shortest_paths(self):
        for src in self.hosts:
            for dst in self.hosts:
                if src != dst:
                    self.logger.info("Computing shortest path from %s to %s",
                                    src, dst)
                    src_switch = self.hosts[src]
                    dst_switch = self.hosts[dst]
                    if nx.has_path(self.graph, src_switch, dst_switch):
                        path = nx.shortest_path(self.graph, src_switch, dst_switch, weight='weight')
                        self.paths[(src, dst)] = path
                        self.logger.info("Shortest path from %s to %s: %s",src, dst, path)
                    else:
                        self.logger.info("There is no path from %s to %s",src, dst)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Ignore LLDP packets
            return

        dst_mac = eth.dst
        src_mac = eth.src

        self.logger.info("Packet in switch %s from %s to %s (in port %s)",
                        datapath.id, src_mac, dst_mac, in_port)

        self.hosts[src_mac] = datapath.id

        if dst_mac in self.hosts:
            # The destination is a host
            out_port = self.get_out_port(datapath, dst_mac)

            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port,
                                    eth_dst=dst_mac,
                                    eth_src=src_mac)
            self.add_flow(datapath, 2, match, actions)
            self.send_packet(datapath, actions, pkt, in_port)
        else:
            # The destination is another switch
            if dst_mac not in self.switches:
                # The destination switch is not in the network
                self.logger.warning("Switch %s not found in the network",
                                    dst_mac)
                return

            out_port = self.get_out_port(datapath, dst_mac)

            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port,
                                    eth_dst=dst_mac,
                                    eth_src=src_mac)
            self.add_flow(datapath, 2, match, actions)
            self.send_packet(datapath, actions, pkt, in_port)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                            actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=priority,
                                match=match,
                                instructions=inst,
                                cookie=0,
                                command=ofproto.OFPFC_ADD,
                                idle_timeout=0,
                                hard_timeout=0,
                                flags=0,
                                buffer_id=ofproto.OFP_NO_BUFFER)
        datapath.send_msg(mod)

    def get_path(self, src_mac, dst_mac):
        if (src_mac, dst_mac) in self.paths:
            return self.paths[(src_mac, dst_mac)]
        else:
            return None

    def get_path_cost(self, src_mac, dst_mac):
        if (src_mac, dst_mac) in self.paths:
            path = self.paths[(src_mac, dst_mac)]
            cost = 0
            for i in range(len(path) - 1):
                switch1 = path[i]
                switch2 = path[i + 1]
                cost += self.graph[switch1][switch2]['weight']
            return cost
        else:
            return None

    def get_all_paths(self):
            return self.paths

    def get_out_port(self, datapath, dst_mac):
        src_mac = datapath.id
        if src_mac not in self.graph:
            # The source switch is not in the network
            self.logger.warning("Switch %s not found in the network", src_mac)
            return None

        if dst_mac not in self.graph:
            # The destination switch is not in the network
            self.logger.warning("Switch %s not found in the network", dst_mac)
            return None

        path = self.get_path(src_mac, dst_mac)
        if path is None:
            # There is no path from the source to the destination
            self.logger.warning("There is no path from %s to %s", src_mac,
                                dst_mac)
            return None

        out_port = None
        for i in range(len(path) - 1):
            switch1 = path[i]
            switch2 = path[i + 1]
            link = self.graph[switch1][switch2]
            if link['src'] == src_mac and link['dst'] == dst_mac:
                out_port = link['src_port']
                break
            elif link['src'] == dst_mac and link['dst'] == src_mac:
                out_port = link['dst_port']
                break

        if out_port is None:
            # The link between the switches was not found
            self.logger.warning("Link between %s and %s not found", src_mac,
                                dst_mac)

        return out_port

    def send_packet(self, datapath, actions, pkt, in_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt.serialize()
        data = pkt.data
        if len(data) > ofproto.OFP_PACKET_IN_MAX_LEN:
            self.logger.warning("Packet is too long")
            return

        out = parser.OFPPacketOut(datapath=datapath,
                                buffer_id=ofproto.OFP_NO_BUFFER,
                                in_port=in_port,
                                actions=actions,
                                data=data)
        datapath.send_msg(out)

