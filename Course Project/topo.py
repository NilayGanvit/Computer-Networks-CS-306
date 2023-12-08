"""
               h1  h2
                |   |
                s9  s10
                 |   |
         s1------s2 s3------s4
         |        | |        |
        s5        s6        s7
         |        | |        |
         s8-------s0--------s11
                |   |
                h3  h4
"""
from collections import defaultdict
from heapq import heappush, heappop
import random

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.node import OVSSwitch, RemoteController, OVSController
from mininet.link import TCLink

class MyTopo(Topo):
    def __init__(self, **opts):
        super().__init__(**opts)

    def build(self):
        switches = []
        hosts = []
        for i in range(1, 11):
            switch = self.addSwitch(f's{i}')
            switches.append(switch)
            host = self.addHost(f'h{i}')
            hosts.append(host)
            self.addLink(host, switch, bw=50, delay=f"{random.randint(1,5)}ms")
        
        self.addLink(switches[0], switches[1], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[0], switches[2], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[0], switches[3], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[1], switches[4], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[1], switches[5], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[2], switches[4], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[2], switches[5], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[3], switches[5], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[3], switches[6], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[4], switches[7], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[4], switches[8], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[5], switches[8], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[5], switches[9], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[6], switches[9], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[7], switches[9], bw=50, delay=f"{random.randint(1,5)}ms")
        self.addLink(switches[8], switches[9], bw=50, delay=f"{random.randint(1,5)}ms")

# topos = { 'mytopo': ( lambda: MyTopo() ) }

def dijkstra(graph, start, end):
    pq = []
    heappush(pq, (0, start, [start]))
    visited = set()

    while pq:
        cost, node, path = heappop(pq)
        if node not in visited:
            visited.add(node)
            path.append(node)
            if node == end:
                return path
            for neighbor in graph[node]:
                if neighbor not in visited:
                    heappush(pq, (cost + graph[node][neighbor], neighbor, path + [neighbor]))
    return []

if __name__ == '__main__':
    setLogLevel('info')
    # create topology
    topo = MyTopo()
    # topos = { 'mytopo': ( lambda: MyTopo() ) }

    # create network with topology and default controller
    net = Mininet(topo=topo,switch=OVSSwitch,controller=OVSController,link=TCLink)
    # net = Mininet(topo=topo, switch=OVSSwitch, controller=RemoteController, link=TCLink)
    # net = Mininet(topo=topos['mytopo'](), switch=OVSSwitch, controller=RemoteController, link=TCLink)

    # start network
    net.start()

    # wait for switches to connect to controller
    print('Waiting for switches to connect to controller...')
    net.waitConnected()

    # discover topology
    switches = []
    hosts = []
    graph = defaultdict(dict)

    for switch_obj in net.switches:
        switch_name=switch_obj
        switches.append(switch_name)
        graph[switch_name] = {}

        for intf_name in switch_obj.intfNames():
            port=intf_name
            if intf_name.startswith('s'):
                graph[switch_name][intf_name] = 0

    for host_name in net.hosts:
        hosts.append(host_name)
        host_ip = switch_obj.cmd(f"host {host_name} | awk '{{print $1}}'")
        graph[switch_name][host_ip.strip()] = 0

    for host in hosts:
        host.cmd('ping -c 1 8.8.8.8') # to populate ARP cache
        for other_host in hosts:
            if host == other_host:
                continue
            path = dijkstra(graph, host.defaultIntf().ip.split('/')[0], other_host.defaultIntf().ip.split('/')[0])
            if path:
                print(f"Path from {host.name} to {other_host.name}: {path}")

    # get user input
    src_host = input('Enter source host: ')
    dst_host = input('Enter destination host: ')
    service_request = input('Enter service request (IPv4 or MAC): ')
    bandwidth = int(input('Enter bandwidth (1-5Mb): '))

    # add flow
    src_ip = net.hosts[int(src_host[-1])-1].defaultIntf().ip.split('/')[0]
    dst_ip = net.hosts[int(dst_host[-1])-1].defaultIntf().ip.split('/')[0]
    src_port = random.randint(10000, 60000)
    dst_port = random.randint(10000, 60000)
    flow_cmd = f"ovs-ofctl add-flow s1 in_port=1,ip,nw_src={src_ip},nw_dst={dst_ip},tp_src={src_port},tp_dst={dst_port},actions=output:2"
    net.get('s1').cmd(flow_cmd)

    # wait for flow to establish
    input('Press Enter to establish connection...')

    # test connection
    if service_request.lower() == 'ipv4':
        net.get(src_host).cmd(f"iperf -c {dst_ip} -t 10 -b {bandwidth}M")
    elif service_request.lower() == 'mac':
        net.get(src_host).cmd(f"iperf -c {dst_host} -t 10 -b {bandwidth}M")
    else:
        print('Invalid service request')

    # stop network
    net.stop()