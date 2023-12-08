from random import randint

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo

file = open("values.txt", "w")


def gen_value(val=None):
    if val is None:
        val = randint(1, 5)
    file.write(f"{val} ")
    return val


class Topology(Topo):
    def build(self):
        switches = []
        hosts = []

        for i in range(1, 10):
            switch = self.addSwitch(f"s{i}")
            switches.append(switch)
            host = self.addHost(f"h{i}")
            hosts.append(host)
            self.addLink(host, switch, bw=gen_value(), delay=f"{gen_value()}ms")
            file.write("\n")

        file.write("0 2 ")
        self.addLink(switches[0], switches[2], bw=gen_value(5), delay=gen_value(5))
        file.write("\n1 2 ")
        self.addLink(switches[1], switches[2], bw=gen_value(5), delay=gen_value(2))
        file.write("\n1 3 ")
        self.addLink(switches[1], switches[3], bw=gen_value(5), delay=gen_value(4))
        file.write("\n2 3 ")
        self.addLink(switches[2], switches[3], bw=gen_value(5), delay=gen_value(1))
        file.write("\n2 4 ")
        self.addLink(switches[2], switches[4], bw=gen_value(5), delay=gen_value(4))
        file.write("\n3 7 ")
        self.addLink(switches[3], switches[7], bw=gen_value(5), delay=gen_value(3))
        file.write("\n3 5 ")
        self.addLink(switches[3], switches[5], bw=gen_value(5), delay=gen_value(3))
        file.write("\n4 5 ")
        self.addLink(switches[4], switches[5], bw=gen_value(5), delay=gen_value(3))
        file.write("\n5 6 ")
        self.addLink(switches[5], switches[6], bw=gen_value(5), delay=gen_value(4))
        file.write("\n6 7 ")
        self.addLink(switches[6], switches[7], bw=gen_value(5), delay=gen_value(2))
        file.write("\n6 8 ")
        self.addLink(switches[6], switches[8], bw=gen_value(5), delay=gen_value(2))
        


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


if __name__ == "__main__":
    setLogLevel("info")
    createNetwork()
