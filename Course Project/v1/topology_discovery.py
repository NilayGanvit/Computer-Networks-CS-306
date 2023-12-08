from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import ethernet
from ryu.lib.packet import packet
from ryu.lib.packet import arp
import networkx as nx
from ryu.lib.packet import ether_types

class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [1.3]

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        self.graph = nx.Graph()
        self.hosts = {}

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        if eth_pkt.ethertype == ether_types.ETH_TYPE_ARP:
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

            self.graph.add_edge(src_mac, dst_mac, weight=1)

            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions)
            datapath.send_msg(out)

    def compute_shortest_paths(self):
        paths = {}
        for src_mac in self.hosts:
            for dst_mac in self.hosts:
                if src_mac == dst_mac:
                    continue
                if nx.has_path(self.graph, src_mac, dst_mac):
                    path = nx.shortest_path(self.graph, src_mac, dst_mac)
                    paths[(src_mac, dst_mac)] = path
        return paths
