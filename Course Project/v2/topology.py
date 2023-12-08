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

        for i in range(1, 7):
            switch = self.addSwitch(f"s{i}")
            switches.append(switch)
            host = self.addHost(f"h{i}")
            hosts.append(host)
            self.addLink(host, switch, bw=gen_value(), delay=f"{gen_value()}ms")
            file.write("\n")

        file.write("0 1 ")
        self.addLink(switches[0], switches[1], bw=gen_value(5), delay=gen_value())
        file.write("\n0 2 ")
        self.addLink(switches[0], switches[2], bw=gen_value(5), delay=gen_value())
        file.write("\n1 2 ")
        self.addLink(switches[1], switches[2], bw=gen_value(5), delay=gen_value())
        file.write("\n1 3 ")
        self.addLink(switches[1], switches[3], bw=gen_value(5), delay=gen_value())
        file.write("\n1 4 ")
        self.addLink(switches[1], switches[4], bw=gen_value(5), delay=gen_value())
        file.write("\n2 4 ")
        self.addLink(switches[2], switches[4], bw=gen_value(5), delay=gen_value())
        file.write("\n3 4 ")
        self.addLink(switches[3], switches[4], bw=gen_value(5), delay=gen_value())
        file.write("\n3 5 ")
        self.addLink(switches[3], switches[5], bw=gen_value(5), delay=gen_value())
        file.write("\n4 5 ")
        self.addLink(switches[4], switches[5], bw=gen_value(5), delay=gen_value())


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
