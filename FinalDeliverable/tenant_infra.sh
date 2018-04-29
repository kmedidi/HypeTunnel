
########################### SHELL SCRIPT TO CREATE INITIAL TENANT INFRASTRUCTURE PER HYPERVISOR ################################
#!/bin/bash
id=$1
create_flag=$2
if [ "$create_flag" == "true" ]
then
netns_name=T"$id"_NS
sudo ip netns add $netns_name
sudo ip link add T"$id"NS_hyp type veth peer name hyp_T"$id"NS
sudo ip link set T"$id"NS_hyp up
sudo ip link set hyp_T"$id"NS up
sudo ip addr add 10.0."$id".2/24 dev hyp_T"$id"NS
sudo ip link set T"$id"NS_hyp netns T"$id"_NS
sudo ip netns exec T"$id"_NS ip link set T"$id"NS_hyp up
sudo ip netns exec T"$id"_NS ip addr add 10.0."$id".1/24 dev T"$id"NS_hyp
sudo ip netns exec T"$id"_NS sudo iptables -t nat -A POSTROUTING -o T"$id"NS_hyp -j MASQUERADE
sudo ip netns exec T"$id"_NS ip route add default via 10.0."$id".2
sudo iptables -t nat -A POSTROUTING -s 10.0."$id".0/24 -j MASQUERADE
flag=$(sudo ip netns exec T"$id"_NS ip addr | grep -c 10.0."$id".1/24)
if [ $flag -eq 1 ]
then
echo "True"
else 
echo "False"
fi
else
sudo ip netns del T"$id"_NS
echo "True"
fi
