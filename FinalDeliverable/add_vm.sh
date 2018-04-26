#!/bin/#!/usr/bin/env bash
#Shell script to create a docker container and add an interface and corresponding flow in central_ovs

#----------------------------------------------------------------------
# Author: Janci https://stackoverflow.com/questions/15429420/given-the-ip-and-netmask-how-can-i-calculate-the-network-address-using-bash
IFS=. read -r i1 i2 i3 i4 <<< $(echo $1 | cut -d/ -f1)
PREFIX=$(echo $1 | cut -d/ -f2)
IFS=. read -r xx m1 m2 m3 m4 <<< $(for a in $(seq 1 32); do if [ $(((a - 1) % 8)) -eq 0 ]; then echo -n .; fi; if [ $a -le $PREFIX ]; then echo -n 1; else echo -n 0; fi; done)
GW=$(printf "%d.%d.%d.%d\n" "$((i1 & (2#$m1)))" "$((i2 & (2#$m2)))" "$((i3 & (2#$m3)))" "$((i4 & (2#$m4))+1)")
#-----------------------------------------------------------------------

#Create container if it doesn't exist
vm_dup=$(sudo docker ps -a | grep -c $1)
if [[ vm_dup -eq 0 ]]
then
  sudo docker run -d --name $1 ubuntu sleep infinity
  #Create veth pair and attach it to the central_ovs and container
  sudo ip link add $1_0 type veth peer name $1_1
  sudo ip link set $1_0 up
  sudo ovs-vsctl add-port central_ovs $1_0 tag=$3
  pid="$(sudo docker inspect -f '{{.State.Pid}}' "$1")"
  sudo ip link set netns $(pid) dev $1_1
  sudo nsenter -t $(pid) -n ip link set $1_1 up
  sudo nsenter -t $(pid) -n ip addr add $2 dev $1_1
  sudo nsenter -t $(pid) -n ip route del default
  sudo nsenter -t $(pid) -n ip route add default via $GW dev $1_1

#Add a flow entry in central_ovs with the mac using $3 - tenantid
fi
