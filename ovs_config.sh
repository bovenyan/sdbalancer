sudo ovs-ofctl del-flows s0 -O OpenFlow13
sudo ovs-ofctl del-flows s1 -O OpenFlow13
sudo ovs-ofctl del-groups s1 -O OpenFlow13
sudo ovs-ofctl del-flows s2 -O OpenFlow13
sudo ovs-ofctl del-flows s3 -O OpenFlow13
sudo ovs-ofctl del-flows s4 -O OpenFlow13

# for port-MAC mapping
for i in `seq 1 10`;
do
    #s0   port->MAC
    udp_port=$(($i+5000))
    dl_dst="00:00:00:00:"$(printf "%02d" $((udp_port/100)))":"$(printf "%02d" $((udp_port%100)))

    sudo ovs-ofctl -O OpenFlow13 add-flow s0 priority=10,in_port=1,ip,udp,tp_dst=$udp_port,actions=mod_dl_dst:$dl_dst,output:2
    
done

sudo ovs-ofctl -O OpenFlow13 add-flow s4 priority=0,in_port=1,actions=mod_dl_dst="00:00:00:00:00:02",output:3
sudo ovs-ofctl -O OpenFlow13 add-flow s4 priority=0,in_port=2,actions=mod_dl_dst="00:00:00:00:00:02",output:3
sudo ovs-ofctl -O OpenFlow13 add-flow s0 priority=0,in_port=1,actions=output:2
sudo ovs-ofctl -O OpenFlow13 add-flow s0 priority=0,in_port=2,actions=output:1

sudo ovs-ofctl dump-flows s0 -O OpenFlow13
sudo ovs-ofctl dump-flows s4 -O OpenFlow13

# for h0-h1-h2 (hash)
sudo ovs-ofctl -O OpenFlow13 add-group s1 group_id=1,type=select,bucket=output:2,bucket=output:3 
sudo ovs-ofctl add-flow s1 priority=0,in_port=1,actions=group:1 -O OpenFlow13

sudo ovs-ofctl add-flow s2 priority=0,in_port=1,actions=output:2 -O OpenFlow13
sudo ovs-ofctl add-flow s3 priority=0,in_port=1,actions=output:2 -O OpenFlow13

sudo ovs-ofctl add-flow s4 priority=0,in_port=1,actions=output:3 -O OpenFlow13
sudo ovs-ofctl add-flow s4 priority=0,in_port=2,actions=output:3 -O OpenFlow13

# for h2-h1 (ARP)
sudo ovs-ofctl add-flow s1 priority=0,in_port=2,actions=output:1 -O OpenFlow13
sudo ovs-ofctl add-flow s2 priority=0,in_port=2,actions=output:1 -O OpenFlow13
sudo ovs-ofctl add-flow s4 priority=0,in_port=3,actions=output:1 -O OpenFlow13

sudo ovs-ofctl dump-flows s1 -O OpenFlow13
sudo ovs-ofctl dump-groups s1 -O OpenFlow13
