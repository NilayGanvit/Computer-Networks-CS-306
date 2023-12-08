from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
# from ryu.lib import hub
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_0_parser
#importing heappush
from heapq import heappush, heappop
#importing event
from ryu.topology import event,switches
#importing random
import random

class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    # _CONTEXTS = {'hub': hub.Hub}

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        self.mac_to_port = {}
        self.paths = {}
        self.graph = {}
        # self.monitor_thread = self.hub.start()
        # self.discover_thread = hub.spawn(self.discover_network)
        self.logger.info("Controller started")

    def discover_network(self):
        while True:
            self.get_topology_data()
            self.logger.info("Topology discovered")
            # hub.sleep(10)

    def get_topology_data(self):
        links = self.topology_api_app.get_switch_links()
        switches = self.topology_api_app.get_switches()

        # Clear the existing topology data
        self.graph = {}
        self.mac_to_port = {}
        self.paths = {}

        # Build the topology graph and mac to port table
        for link in links:
            src_mac = link.src.dpid
            dst_mac = link.dst.dpid
            src_port = link.src.port_no
            dst_port = link.dst.port_no

            if src_mac not in self.graph:
                self.graph[src_mac] = {}
                self.mac_to_port[src_mac] = {}

            if dst_mac not in self.graph:
                self.graph[dst_mac] = {}
                self.mac_to_port[dst_mac] = {}

            # Add link to graph
            self.graph[src_mac][dst_mac] = {'src': src_mac, 'dst': dst_mac,
                                             'src_port': src_port,
                                             'dst_port': dst_port,
                                             'delay': self.get_link_delay(src_mac, dst_mac),
                                             'bw': 50}
            self.graph[dst_mac][src_mac] = {'src': dst_mac, 'dst': src_mac,
                                             'src_port': dst_port,
                                             'dst_port': src_port,
                                             'delay': self.get_link_delay(dst_mac, src_mac),
                                             'bw': 50}

            # Add MAC to port mappings
            self.mac_to_port[src_mac][link.src.port_no] = link.dst.dpid
            self.mac_to_port[dst_mac][link.dst.port_no] = link.src.dpid

        # Compute shortest paths for all pairs of hosts in the network
        for src in switches:
            for dst in switches:
                if src.dp.id != dst.dp.id:
                    path = self.get_path(src.dp.id, dst.dp.id)
                    if path:
                        self.paths[(src.dp.id, dst.dp.id)] = path

    def get_link_delay(self, src, dst):
        return self.graph[src][dst]['delay']

    def get_path(self, src, dst):
        if src not in self.graph:
            self.logger.warning("Switch %s not found in the network", src)
            return None

        if dst not in self.graph:
            self.logger.warning("Switch %s not found in the network", dst)
            return None

        visited = {src: 0}
        path = {}
        nodes = list(self.graph.keys())
        while nodes:
            min_node = None
            for node in nodes:
                if node in visited:
                    if min_node is None:
                        min_node = node
                    elif visited[node] < visited[min_node]:
                        min_node = node

            if min_node is None:
                break

            nodes.remove(min_node)
            current_cost = visited[min_node]

            for neighbor in self.graph[min_node]:
                cost = current_cost + self.graph[min_node][neighbor]['delay']
                if neighbor not in visited or cost < visited[neighbor]:
                    visited[neighbor] = cost
                    if neighbor == dst:
                        path = [dst]
                        while dst != src:
                            for hop in self.graph[src][dst]['prev']:
                                if hop in visited and visited[hop] == visited[dst] - self.graph[hop][dst]['delay']:
                                    path.insert(0, hop)
                                    dst = hop
                                    break
                        return path

                    self.graph[src][neighbor]['prev'] = [min_node]
                    visited[neighbor] = cost

        self.logger.warning("No path found between %s and %s", src, dst)
        return None

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()

        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

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

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        # Get the datapath of the switch
        dpid = datapath.id

        # Learn the MAC address to avoid FLOOD next time.
        self.mac_to_port[dpid][msg.in_port] = dst

        # If the source is not a host, then don't forward it
        if src not in self.mac_to_port[dpid]:
            return

        # Find the port to forward the packet to
        out_port = self.get_out_port(datapath, src, dst, msg.in_port)

        # If the destination is a host, then install a flow rule
        # to forward future packets directly to the host
        if out_port and dst in self.mac_to_port[dpid]:
            match = parser.OFPMatch(in_port=msg.in_port, eth_dst=dst)
            actions = [parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)

        # Send the packet to the correct switch port
        if out_port:
            data = None
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                    in_port=msg.in_port, actions=actions, data=data)
            datapath.send_msg(out)

    def get_out_port(self, datapath, src, dst, in_port):
        dpid = datapath.id

        # If the destination is a host, then forward it to the host's port
        if dst in self.host_to_port[dpid]:
            return self.host_to_port[dpid][dst]

        # If we don't know the destination, then flood
        elif dst not in self.mac_to_port[dpid]:
            ofproto = datapath.ofproto
            return ofproto.OFPP_FLOOD

        # Otherwise, find the shortest path to the destination
        else:
            path = self.dijkstra(src, dst)
            if path:
                next_hop = path[0]
                return self.graph[dpid][next_hop]['port']
            else:
                return None
    
    def dijkstra(self, src, dst):
        """Dijkstra's algorithm to find the shortest path from src to dst
        """
        heap = []
        heappush(heap, (0, src, []))

        while heap:
            (cost, node, path) = heappop(heap)
            if node == dst:
                return path + [node]

            if node in self.graph:
                for neighbor, link in self.graph[node].items():
                    if neighbor not in path:
                        heappush(heap, (cost + link['cost'], neighbor, path + [node]))

        return None

    @set_ev_cls(event.EventHostAdd)
    def host_add_handler(self, ev):
        """
        Update the MAC address to port mapping for the host
        """
        host = ev.host
        self.logger.info('Host added: %s', host)

        dpid = host.port.dpid
        mac = host.mac
        port = host.port.port_no

        if dpid not in self.host_to_port:
            self.host_to_port[dpid] = {}

        self.host_to_port[dpid][mac] = port

    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        """
        Update the graph with the new switch information
        """
        switch = ev.switch
        dpid = switch.dp.id

        self.logger.info('Switch entered: %s', dpid)

        if dpid not in self.graph:
            # self.graph.add_node(dpid)
            # adding dpid as node in graph which is a dict
            self.graph[dpid] = {}

    @set_ev_cls(event.EventLinkAdd)
    def link_add_handler(self, ev):
        """
        Update the graph with the new link information
        """
        link = ev.link
        src_dpid = link.src.dpid
        dst_dpid = link.dst.dpid
        src_port = link.src.port_no
        dst_port = link.dst.port_no
        delay = random.randint(1, 5)  # random delay between 1ms and 5ms

        self.logger.info('Link added: %s -> %s', src_dpid, dst_dpid)

        if src_dpid not in self.graph:
            # self.graph.add_node(src_dpid)
            # adding src_dpid as node in graph which is a dict
            self.graph[src_dpid] = {}
        if dst_dpid not in self.graph:
            # self.graph.add_node(dst_dpid)
            # adding dst_dpid as node in graph which is a dict
            self.graph[dst_dpid] = {}

        self.graph.add_edge(src_dpid, dst_dpid, port=src_port, cost=delay)
        self.graph.add_edge(dst_dpid, src_dpid, port=dst_port, cost=delay)

    @set_ev_cls(event.EventSwitchLeave)
    def switch_leave_handler(self, ev):
        """
        Remove the switch information from the graph
        """
        switch = ev.switch
        dpid = switch.dp.id

        self.logger.info('Switch left: %s', dpid)

        if dpid in self.graph:
            self.graph.remove_node(dpid)

    @set_ev_cls(event.EventLinkDelete)
    def link_delete_handler(self, ev):
        """
        Remove the link information from the graph
        """
        link = ev.link
        src_dpid = link.src.dpid
        dst_dpid = link.dst.dpid

        self.logger.info('Link deleted: %s -> %s', src_dpid, dst_dpid)

        if src_dpid in self.graph and dst_dpid in self.graph[src_dpid]:
            self.graph.remove_edge(src_dpid, dst_dpid)
        if dst_dpid in self.graph and src_dpid in self.graph[dst_dpid]:
            self.graph.remove_edge(dst_dpid, src_dpid)