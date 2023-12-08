from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.cli import CLI


class Topology(Topo):
    def build(self, n=2):
        switch = self.addSwitch("s1")
        for h in range(n):
            host = self.addHost(f"h{h+1}")
            self.addLink(host, switch, bw=50, delay="20ms", cls=TCLink)


def createNetwork():
    "Create and test a simple network"
    topo = Topology(n=3)
    net = Mininet(topo, controller=RemoteController, autoSetMacs=True)
    net.start()

    # net.iperf()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    createNetwork()
