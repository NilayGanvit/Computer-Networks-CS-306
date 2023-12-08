"""Custom topology example

Ten connected switches plus a host for each switch:

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        firstHost = self.addHost( 'h1' )
        secondHost = self.addHost( 'h2' )
        thirdHost = self.addHost( 'h3' )
        fourthHost = self.addHost( 'h4' )
        fifthHost = self.addHost( 'h5' )
        sixthHost = self.addHost( 'h6' )
        seventhHost = self.addHost( 'h7' )
        eighthHost = self.addHost( 'h8' )
        ninthHost = self.addHost( 'h9' )
        tenthHost = self.addHost( 'h10' )
        firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )
        thirdSwitch = self.addSwitch( 's3' )
        fourthSwitch = self.addSwitch( 's4' )
        fifthSwitch = self.addSwitch( 's5' )
        sixthSwitch = self.addSwitch( 's6' )
        seventhSwitch = self.addSwitch( 's7' )
        eighthSwitch = self.addSwitch( 's8' )
        ninthSwitch = self.addSwitch( 's9' )
        tenthSwitch = self.addSwitch( 's10' )
        
        # Add links
        self.addLink( firstHost, firstSwitch )
        self.addLink( secondHost, secondSwitch )
        self.addLink( thirdHost, thirdSwitch )
        self.addLink( fourthHost, fourthSwitch )
        self.addLink( fifthHost, fifthSwitch )
        self.addLink( sixthHost, sixthSwitch )
        self.addLink( seventhHost, seventhSwitch )
        self.addLink( eighthHost, eighthSwitch )
        self.addLink( ninthHost, ninthSwitch )
        self.addLink( tenthHost, tenthSwitch )
        self.addLink( firstSwitch, secondSwitch )
        self.addLink( firstSwitch, thirdSwitch )
        self.addLink( secondSwitch, fourthSwitch )
        self.addLink( secondSwitch, fifthSwitch )
        self.addLink( thirdSwitch, sixthSwitch )
        self.addLink( thirdSwitch, seventhSwitch )
        self.addLink( fourthSwitch, eighthSwitch )
        self.addLink( fourthSwitch, ninthSwitch )
        self.addLink( fifthSwitch, tenthSwitch )


topos = { 'mytopo': ( lambda: MyTopo() ) }
