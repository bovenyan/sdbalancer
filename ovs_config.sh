sudo ovs-vsctl set bridge s1 protocols=OpenFlow13
sudo ovs-vsctl set bridge s2 protocols=OpenFlow13
sudo ovs-vsctl set bridge s3 protocols=OpenFlow13
sudo ovs-vsctl set bridge s4 protocols=OpenFlow13

sudo ovs-ofctl del-flows s1 -O OpenFlow13
sudo ovs-ofctl del-flows s2 -O OpenFlow13
sudo ovs-ofctl del-flows s3 -O OpenFlow13
sudo ovs-ofctl del-flows s4 -O OpenFlow13

sudo ovs-ofctl -O OpenFlow13 add-group s1 group_id=1,type=select,bucket=bucket=output:2,bucket=output:3 
sudo ovs-ofctl add-flow s1 priority=0,in_port=1,actions=group:1 -O OpenFlow13

sudo ovs-ofctl add-flow s2 priority=0,in_port=1,actions=output:2 -O OpenFlow13
sudo ovs-ofctl add-flow s3 priority=0,in_port=1,actions=output:2 -O OpenFlow13

sudo ovs-ofctl add-flow s4 priority=0,in_port=1,actions=output:3 -O OpenFlow13
sudo ovs-ofctl add-flow s4 priority=0,in_port=2,actions=output:3 -O OpenFlow13
