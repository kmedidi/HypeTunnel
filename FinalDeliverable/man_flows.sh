#!/bin/bash
if [[ $1 == "true" ]]
then
out_int=$(sudo ovs-vsctl show | grep -B 2 $2 | grep Interface\ \"vxlan | cut -d '"' -f 2)
out_port=$(sudo ovs-ofctl show tunnel_ovs | grep $out_int | cut -d '(' -f 1 | cut -d ' ' -f 2)
sudo ovs-ofctl add-flow tunnel_ovs "table=1,tun_id=$3,dl_dst=$4,actions=output:$out_port"
sudo ovs-ofctl add-flow tunnel_ovs "table=1,tun_id=$3,arp,nw_dst=$(echo $5 | cut -d '/' -f 1),actions=output:$out_port"
ip_ad=$(echo $5 | cut -d '/' -f 1)
sudo ip netns exec T$3_NS arp -s $ip_ad $4
elif [[ $1 == "false" ]]
then
ip_ad=$(echo $5 | cut -d '/' -f 1)
sudo ovs-ofctl del-flows tunnel_ovs "tun_id=$3,dl_dst=$4"
sudo ovs-ofctl del-flows tunnel_ovs "tun_id=$3,ip,nw_dst=$ip_ad"
sudo ovs-ofctl del-flows tunnel_ovs "tun_id=$3,arp,nw_dst=$ip_ad"
sudo ip netns exec T$3_NS arp -d $ip_ad
fi
