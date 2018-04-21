#!/bin/bash
#Create directories $HOME/HypeTunnel, $HOME/HypeTunnel/conf, $HOME/HypeTunnel/logs
sudo mkdir -p -- $HOME/HypeTunnel/conf
sudo mkdir -p -- $HOME/HypeTunnel/logs

# Create files $HOME/HypeTunnel/conf/flows.txt, $HOME/HypeTunnel/logs/logs.txt
sudo touch -a $HOME/HypeTunnel/conf/flows.txt
sudo touch -a $HOME/HypeTunnel/logs/logs.txt

# Create central_ovs if absent
cpresent=$(sudo ovs-vsctl show | grep -cw central_ovs)
if ! [[ $cpresent -gt 0 ]]
then
  sudo ovs-vsctl add-br central_ovs
fi

# Create tunnel_ovs if absent
tpresent=$(sudo ovs-vsctl show | grep -cw tunnel_ovs)
if ! [[ $tpresent -gt 0 ]]
then
  sudo ovs-vsctl add-br tunnel_ovs
fi

# Connect tunnel_ovs with central_ovs
t0present=$(sudo ovs-vsctl show | grep -cw tunn0)
t1present=$(sudo ovs-vsctl show | grep -cw tunn1)
if ! [[ $t0present -gt 0 && $t1present -gt 0 ]]
then
  sudo ip link add tunn0 type veth peer name tunn1
  sudo ip link set tunn0 up
  sudo ip link set tunn1 up
  sudo ovs-vsctl add-port central_ovs tunn0 -- set Interface tunn0 ofport=1
  sudo ovs-vsctl add-port tunnel_ovs tunn1 -- set Interface tunn1 ofport=10
fi

# Getting local ip
my_ip=$1

# Create VXLAN & GRE tunnel interfaces
i=1
for var in "$@"
do
  if ! [[ $i -lt 2 ]]
  then
    ipresent=$(sudo ovs-vsctl show | grep -cw $var)
    if ! [[ $ipresent -gt 0 ]]
    then
      vxlan_int_name=$i
      gre_int_name=$i
      vxlan_int=$(($i+10))
      gre_int=$(($i+11))
      ovs-vsctl add-port tunnel_ovs vxlan_$vxlan_int_name -- set Interface vxlan_$i ofport_request=$vxlan_int type=vxlan options:local_ip=$my_ip options:remote_ip=$var
      ovs-vsctl add-port tunnel_ovs gre_$gre_int_name -- set Interface gre_$i ofport_request=$gre_int type=gre options:remote_ip=$var
    fi
  fi
  i=$(($i+1))
done
