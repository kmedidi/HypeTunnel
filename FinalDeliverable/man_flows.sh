#!/bin/bash
if [[ $1 -eq "true" ]]
then
out_int=$(sudo ovs-vsctl show | grep -B 2 -m 1 $2 | grep Interface | cut -d '"' -f 2)
out_port=$(sudo ovs-ofctl show tunnel_ovs | grep $out_int | cut -d '(' -f 1 | cut -d ' ' -f 2)
sudo ovs-ofctl add-flow tunnel_ovs table=0,in_port=30,dl_dst=$3,actions=output:$out_port
sudo ovs-ofctl add-flow tunnel_ovs table=0,in_port=30,arp,nw_dst=$4,actions=output:$out_port
else
sudo ovs-ofctl del-flows tunnel_ovs dl_dst=$3
sudo ovs-ofctl del-flows tunnel_ovs nw_dst=$4
fi
