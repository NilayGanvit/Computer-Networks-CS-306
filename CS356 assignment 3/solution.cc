
#include <fstream>
#include "ns3/core-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/mobility-module.h"
#include "ns3/netanim-module.h"
#include "ns3/network-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("UdpClientServerExample");

int main(int argc, char *argv[])
{
    // Declare variables used in command-line arguments
    bool useV6 = false;
    bool logging = false;
    Address server_Addresses_1, server_Addresses_2;

    CommandLine cmd(__FILE__);
    cmd.AddValue("useIpv6", "Use Ipv6", useV6);
    cmd.AddValue("logging", "Enable logging", logging);
    cmd.Parse(argc, argv);

    if (logging)
    {
        LogComponentEnable("UdpClient", LOG_LEVEL_INFO);
        LogComponentEnable("UdpServer", LOG_LEVEL_INFO);
        LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_ALL);
        LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_ALL);
    }

    NS_LOG_INFO("Create nodes in above LAN1 topology.");
    NodeContainer n;
    n.Create(2);

    NS_LOG_INFO("Create nodes in above LAN2 topology.");
    NodeContainer m;
    m.Create(4);

    MobilityHelper mobility1;
    Ptr<ListPositionAllocator> enbPositionAlloc1 = CreateObject<ListPositionAllocator>();
    enbPositionAlloc1->Add(Vector(0, 50, 0));
    enbPositionAlloc1->Add(Vector(0, 25, 0));
    mobility1.SetPositionAllocator(enbPositionAlloc1);
    mobility1.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility1.Install(n);

    MobilityHelper mobility2;
    Ptr<ListPositionAllocator> enbPositionAlloc2 = CreateObject<ListPositionAllocator>();
    enbPositionAlloc2->Add(Vector(100, 25, 0));
    enbPositionAlloc2->Add(Vector(75, 25, 0));
    enbPositionAlloc2->Add(Vector(75, 50, 0));
    enbPositionAlloc2->Add(Vector(100, 50, 0));
    mobility2.SetPositionAllocator(enbPositionAlloc2);
    mobility2.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility2.Install(m);

    InternetStackHelper internet1;
    internet1.Install(n);

    InternetStackHelper internet2;
    internet2.Install(m);

    NS_LOG_INFO("Create channel between the two nodes.");
    CsmaHelper csma;
    csma.SetChannelAttribute("DataRate", DataRateValue(DataRate(5000000)));
    csma.SetChannelAttribute("Delay", TimeValue(MilliSeconds(2)));
    csma.SetDeviceAttribute("Mtu", UintegerValue(1400));
    NetDeviceContainer d1 = csma.Install(n);
    NetDeviceContainer d2 = csma.Install(m);

    NS_LOG_INFO("Assign IP Addresses.");
    if (useV6 == false)
    {
        Ipv4AddressHelper ipv4;
        ipv4.SetBase("130.20.0.0", "255.255.255.0");
        Ipv4InterfaceContainer i1 = ipv4.Assign(d1);
        server_Addresses_1 = Address(i1.GetAddress(1));

        ipv4.SetBase("130.30.0.0", "255.255.255.0");
        Ipv4InterfaceContainer i2 = ipv4.Assign(d2);
        server_Addresses_2 = Address(i2.GetAddress(3));
    }
    else
    {
        Ipv6AddressHelper ipv6;
        ipv6.SetBase("2001:0000:f00d:cafe::", Ipv6Prefix(64));
        Ipv6InterfaceContainer i6_1 = ipv6.Assign(d1);
        server_Addresses_1 = Address(i6_1.GetAddress(1, 1));
        ipv6.SetBase("2001:0000:f00d:cafd::", Ipv6Prefix(64));
        Ipv6InterfaceContainer i6_2 = ipv6.Assign(d2);
        server_Addresses_2 = Address(i6_2.GetAddress(1, 1));
    }

    NS_LOG_INFO("Create UdpServer application LAN1 on node 1.");
    uint16_t port1 = 4000;
    UdpServerHelper server1(port1);
    ApplicationContainer apps1 = server1.Install(n.Get(1));
    apps1.Start(Seconds(1.0));
    apps1.Stop(Seconds(10.0));

    NS_LOG_INFO("Create UdpServer application LAN2 on node 3.");
    uint16_t port2 = 5000;
    UdpEchoServerHelper server2(port2);
    ApplicationContainer apps2 = server2.Install(m.Get(3));
    apps2.Start(Seconds(1.0));
    apps2.Stop(Seconds(10.0));

    NS_LOG_INFO("Create UdpClient application LAN1 on node 0 to send to node 1.");
    uint32_t MaxPacketSize = 1024;
    Time interPacketInterval = Seconds(1.0);
    uint32_t maxPacketCount = 10;
    UdpClientHelper client1(server_Addresses_1, port1);
    client1.SetAttribute("MaxPackets", UintegerValue(maxPacketCount));
    client1.SetAttribute("Interval", TimeValue(interPacketInterval));
    client1.SetAttribute("PacketSize", UintegerValue(MaxPacketSize));
    apps1 = client1.Install(n.Get(0));
    apps1.Start(Seconds(2.0));
    apps1.Stop(Seconds(10.0));

    NS_LOG_INFO("Create UdpClient application LAN2 on node 1 to send to node 3.");
    interPacketInterval = Seconds(0.5);
    UdpClientHelper client2(server_Addresses_2, port2);
    client2.SetAttribute("MaxPackets", UintegerValue(maxPacketCount));
    client2.SetAttribute("Interval", TimeValue(interPacketInterval));
    client2.SetAttribute("PacketSize", UintegerValue(MaxPacketSize));
    apps2 = client2.Install(m.Get(1));
    apps2.Start(Seconds(2.0));
    apps2.Stop(Seconds(10.0));

    NodeContainer nodes, p2pNode1, p2pNode2;
    nodes.Create(2);
    p2pNode1.Add(n.Get(1));
    p2pNode1.Add(nodes.Get(0));
    p2pNode2.Add(nodes.Get(1));
    p2pNode2.Add(m.Get(0));

    MobilityHelper mobility3_1;
    Ptr<ListPositionAllocator> enbPositionAlloc3_1 = CreateObject<ListPositionAllocator>();
    enbPositionAlloc3_1->Add(Vector(25, 50, 0));
    enbPositionAlloc3_1->Add(Vector(50, 25, 0));
    mobility3_1.SetPositionAllocator(enbPositionAlloc3_1);
    mobility3_1.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility3_1.Install(nodes);

    PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute("DataRate", StringValue("5Mbps"));
    pointToPoint.SetChannelAttribute("Delay", StringValue("2ms"));

    NetDeviceContainer devices, p2pdevice1, p2pdevice2;
    devices = pointToPoint.Install(nodes);
    p2pdevice1 = pointToPoint.Install(p2pNode1);
    p2pdevice1 = pointToPoint.Install(p2pNode2);

    InternetStackHelper stack;
    stack.Install(nodes);

    Ipv4AddressHelper address;
    address.SetBase("130.10.0.0", "255.255.255.0");

    Ipv4InterfaceContainer interfaces = address.Assign(devices);

    UdpEchoServerHelper echoServer(9);

    ApplicationContainer serverApps = echoServer.Install(nodes.Get(1));
    serverApps.Start(Seconds(1.0));
    serverApps.Stop(Seconds(10.0));

    UdpEchoClientHelper echoClient(interfaces.GetAddress(1), 9);
    echoClient.SetAttribute("MaxPackets", UintegerValue(10));
    echoClient.SetAttribute("Interval", TimeValue(Seconds(1.0)));
    echoClient.SetAttribute("PacketSize", UintegerValue(1024));

    ApplicationContainer clientApps = echoClient.Install(nodes.Get(0));
    clientApps.Start(Seconds(2.0));
    clientApps.Stop(Seconds(10.0));

    AnimationInterface anim("output/200001053_ass3.xml");

    anim.EnablePacketMetadata();

    AsciiTraceHelper ascii;
    csma.EnableAsciiAll(ascii.CreateFileStream("output/190001059_ass4.tr"));
    pointToPoint.EnableAsciiAll(ascii.CreateFileStream("output/190001059_ass4_PointToPoint.tr"));
    csma.EnablePcapAll("udp-echo", false);

    NS_LOG_INFO("Run Simulation.");
    Simulator::Run();
    pointToPoint.EnablePcapAll ("solution");
    Simulator::Destroy();
    NS_LOG_INFO("Done.");
}