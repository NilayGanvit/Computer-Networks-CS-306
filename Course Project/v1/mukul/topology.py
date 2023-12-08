from random import randint

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo

file = open("values.txt", "w")


def gen_value():
    val = randint(1, 5)
    file.write(f"{val} ")
    return val


class Topology(Topo):
    def build(self):
        switches = []
        hosts = []

        for i in range(1, 7):
            switch = self.addSwitch(f"s{i}")
            switches.append(switch)
            host = self.addHost(f"h{i}")
            hosts.append(host)
            self.addLink(host, switch, bw=gen_value(), delay=f"{gen_value()}ms")
            file.write("\n")

        file.write("0 1 ")
        self.addLink(switches[0], switches[1], bw=gen_value(), delay=gen_value())
        file.write("\n0 2 ")
        self.addLink(switches[0], switches[2], bw=gen_value(), delay=gen_value())
        file.write("\n1 2 ")
        self.addLink(switches[1], switches[2], bw=gen_value(), delay=gen_value())
        file.write("\n1 3 ")
        self.addLink(switches[1], switches[3], bw=gen_value(), delay=gen_value())
        file.write("\n1 4 ")
        self.addLink(switches[1], switches[4], bw=gen_value(), delay=gen_value())
        file.write("\n2 4 ")
        self.addLink(switches[2], switches[4], bw=gen_value(), delay=gen_value())
        file.write("\n3 4 ")
        self.addLink(switches[3], switches[4], bw=gen_value(), delay=gen_value())
        file.write("\n3 5 ")
        self.addLink(switches[3], switches[5], bw=gen_value(), delay=gen_value())
        file.write("\n4 5 ")
        self.addLink(switches[4], switches[5], bw=gen_value(), delay=gen_value())


def createNetwork():
    "Create and test a simple network"
    topo = Topology()
    file.close()
    net = Mininet(
        topo,
        controller=RemoteController(name="ryu", port=6633),
        autoSetMacs=True,
        switch=OVSSwitch,
        link=TCLink,
    )
    net.start()
    CLI(net)
    net.stop()

# def floyd_warshall(self):
#     for k in range(self.nodes):
#         for i in range(self.nodes):
#             for j in range(self.nodes):
#                 if self.distances[i][j] > self.distances[i][k] + self.distances[k][j]:
#                     self.distances[i][j] = self.distances[i][k] + self.distances[k][j]
#                     self.next_hop[i][j] = k

# def read_graph(self):
#     self.nodes = int(input("Enter number of nodes: "))
#     self.edges = [[1e7 for i in range(self.nodes)] for j in range(self.nodes)]
#     self.distances = [[1e7 for i in range(self.nodes)] for j in range(self.nodes)]
#     self.host_map = {}
#     for i in range(self.nodes):
#         self.host_map[i] = input(f"Enter name of host {i}: ")
#     for i in range(self.nodes):
#         self.edges[i][i] = 0
#         self.distances[i][i] = 0
#     for i in range(self.nodes):
#         for j in range(self.nodes):
#             if i == j:
#                 continue
#             self.edges[i][j] = int(input(f"Enter cost of edge ({i}, {j}): "))
#             self.distances[i][j] = self.edges[i][j]

#     def print_solution(self, src):
#         print(f"Routing table for {self.host_map[src]}")
#         print("Switch\tCost")
#         for i in range(self.nodes):
#             if self.distances[src][i] == 1e7:
#                 print(f"{i}\t∞")
#             else:
#                 print(f"{i}\t{self.distances[src][i]}")

#     def main(self):
#         self.read_graph()
#         self.floyd_warshall()
#         for i in range(self.nodes):
#             self.print_solution(i)

if __name__ == "__main__":
    setLogLevel("info")
    createNetwork()
#     f = FloydWarshall()
#     f.main()