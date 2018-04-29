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
