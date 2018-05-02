#!/bin/bash
IFS=. read -r i1 i2 i3 i4 <<< $(echo $2 | cut -d/ -f1)
PREFIX=$(echo $2 | cut -d/ -f2)
IFS=. read -r xx m1 m2 m3 m4 <<< $(for a in $(seq 1 32); do if [ $(((a - 1) % 8)) -eq 0 ]; then echo -n .; fi; if [ $a -le $PREFIX ]; then echo -n 1; else echo -n 0; fi; done)

GW=$(printf "%d.%d.%d.%d\n" "$((i1 & (2#$m1)))" "$((i2 & (2#$m2)))" "$((i3 & (2#$m3)))" "$((((i4 & (2#$m4)))+1))")
veth1=$(echo $2 | tr -dc '[:alnum:]')

sudo ip link add ot$1_$veth1 type veth peer name t$1o_$veth1
sudo ip link set ot$1_$veth1 up
sudo ip link set t$1o_$veth1 up
sudo ip link set t"$1"o_$veth1 netns T$1_NS
sudo ovs-vsctl add-port central_ovs ot$1_$veth1 tag=$3

trunks=""
for i in `seq 0 100 4000`
do
  range=$(($3-$i))
  if [[ $range -le 100 ]]
  then
    trunkStart=$(($i+1))
    for vlan in `seq $trunkStart $3`
    do
      if ! [[ trunks -eq "" ]]
      then
        trunks=$trunks","$vlan
      else
        trunks=$vlan
      fi
    done
  fi
done
sudo ovs-vsctl set port tunn0 trunks=$trunks
sudo ovs-vsctl set port tunn1 trunks=$trunks

sudo ip link set ot"$1"_$veth1 up
sudo ip netns exec T$1_NS ip link set t"$1"o_$veth1 up
sudo ip netns exec T$1_NS ip address add $GW/$PREFIX dev t"$1"o_$veth1
flag=$(sudo ip netns exec T$1_NS ip address | grep -c $GW)
if [ $flag -eq 1 ]
then
echo "True"
else
echo "False"
fi

sudo ovs-ofctl add-flow tunnel_ovs "table=0,in_port=30,dl_vlan=$3,actions=set_field:$1->tun_id,resubmit(,1)"
sudo ovs-ofctl add-flow tunnel_ovs "table=1,in_port=30,arp,nw_dst=$GW,actions=drop"
sudo ovs-ofctl add-flow tunnel_ovs "table=1,in_port=30,ip,nw_dst=$GW,actions=drop"

Nints=$(sudo ovs-ofctl show tunnel_ovs | grep -c vxlan)
for val in `seq 2 $(($Nints+1))`
do
  vxlanInt=$(sudo ovs-ofctl show tunnel_ovs | grep vxlan_$val | cut -d '(' -f 1 | cut -d ' ' -f 2)
  sudo ovs-ofctl add-flow tunnel_ovs "table=0,in_port=$vxlanInt,tun_id=$1,ip,nw_dst=$GW/$PREFIX,actions=mod_vlan_vid:$3,output:30"
done
