from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, Host, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from functools import partial


class MyTopo(Topo):
    def __init__(self):
        "Create custom topo."
        # Initialize topology
        Topo.__init__(self)
        # Add hosts and switches

        H1 = self.addHost('h1', mac='00:00:00:00:00:01', IP='10.0.0.1')
        H2 = self.addHost('h2', mac='00:00:00:00:00:02', IP='10.0.0.2')
        S0 = self.addSwitch('s0', protocols='OpenFlow13')
        S1 = self.addSwitch('s1', protocols='OpenFlow13')
        S2 = self.addSwitch('s2', protocols='OpenFlow13')
        S3 = self.addSwitch('s3', protocols='OpenFlow13')
        S4 = self.addSwitch('s4', protocols='OpenFlow13')

        # Add links
        self.addLink(H1, S0, bw=100, cls=TCLink) 
        self.addLink(S0, S1, bw=100, cls=TCLink) 
        self.addLink(S1, S2, bw=50, cls=TCLink)
        self.addLink(S1, S3, bw=50, cls=TCLink)
        self.addLink(S2, S4, bw=50, cls=TCLink)
        self.addLink(S3, S4, bw=50, cls=TCLink)
        self.addLink(S4, H2, bw=100, cls=TCLink)


def iperf():
    topo = MyTopo()
    Switch = partial( OVSSwitch, protocols='OpenFlow13')
    net = Mininet(topo=topo, controller=RemoteController, host=Host, link=TCLink)
    net.start()

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    iperf()
