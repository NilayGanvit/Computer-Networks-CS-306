"""Custom topology example

Eight ring connected switches plus a four ring connected switches for first and seventh switches:

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Ring topology example."

    def build(self):
        "Create custom topo."

        # Add hosts and switches
        firstHost = self.addHost('h1')
        secondHost = self.addHost('h2')
        thirdHost = self.addHost('h3')
        fourthHost = self.addHost('h4')
        fifthHost = self.addHost('h5')
        sixthHost = self.addHost('h6')
        seventhHost = self.addHost('h7')
        eighthHost = self.addHost('h8')
        firstSwitch = self.addSwitch('s1')
        secondSwitch = self.addSwitch('s2')
        thirdSwitch = self.addSwitch('s3')
        fourthSwitch = self.addSwitch('s4')
        fifthSwitch = self.addSwitch('s5')
        sixthSwitch = self.addSwitch('s6')
        seventhSwitch = self.addSwitch('s7')
        eighthSwitch = self.addSwitch('s8')
        Host2 = self.addHost('h9')
        Host4 = self.addHost('h10')
        Switch2 = self.addSwitch('s9')
        Switch4 = self.addSwitch('s10')

        # Add links
        self.addLink(firstHost, firstSwitch)
        self.addLink(firstSwitch, secondSwitch)
        self.addLink(secondSwitch, secondHost)
        self.addLink(secondSwitch, thirdSwitch)
        self.addLink(thirdSwitch, thirdHost)
        self.addLink(thirdSwitch, fourthSwitch)
        self.addLink(fourthSwitch, fourthHost)
        self.addLink(fourthSwitch, fifthSwitch)
        self.addLink(fifthSwitch, fifthHost)
        self.addLink(fifthSwitch, sixthSwitch)
        self.addLink(sixthSwitch, sixthHost)
        self.addLink(sixthSwitch, seventhSwitch)
        self.addLink(seventhSwitch, seventhHost)
        self.addLink(seventhSwitch, eighthSwitch)
        self.addLink(eighthSwitch, eighthHost)
        self.addLink(eighthSwitch, firstSwitch)
        self.addLink(firstSwitch, Switch2)
        self.addLink(Host2, Switch2)
        self.addLink(Switch2, seventhSwitch)
        self.addLink(seventhSwitch, Switch4)
        self.addLink(Host4, Switch4)
        self.addLink(Switch4, firstSwitch)

topos = { 'mytopo': ( lambda: MyTopo() ) }