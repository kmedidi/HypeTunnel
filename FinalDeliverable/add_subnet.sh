#!/bin/bash

veth1=$2 | tr -dc '[:alnum:]'
sudo ip link add ot$1_$veth1 type veth peer name to$1_$veth1
sudo ip link set to$1_$veth1 netns t$1_NS
sudo ovs-vsctl add-port central_ovs ot$1_$veth1 tag=$1

sudo ip netns exec t$1_NS ip address add $2 dev to$1_$veth1
sudo ip netns exec t$1_NS ip address | grep -c $2
