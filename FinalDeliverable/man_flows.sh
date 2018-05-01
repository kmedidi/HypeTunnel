#!/bin/bash
if [[ $1 -eq "true" ]]
then
out_int=$(sudo ovs-vsctl show | grep -B 2 192.168.124.229 | grep Interface\ \"vxlan | cut -d '"' -f 2)
out_port=$(sudo ovs-ofctl show tunnel_ovs | grep $out_int | cut -d '(' -f 1 | cut -d ' ' -f 2)
sudo ovs-ofctl add-flow tunnel_ovs table=1,tun_id=$3,dl_dst=$4,actions=output:$out_port
sudo ovs-ofctl add-flow tunnel_ovs table=1,tun_id=$3,arp,nw_dst=$(echo $5 | cut -d '/' -f 1),actions=output:$out_port
else
sudo ovs-ofctl del-flows tunnel_ovs tun_id=$3,dl_dst=$4
sudo ovs-ofctl del-flows tunnel_ovs tun_id=$3,nw_dst=$5
fi
