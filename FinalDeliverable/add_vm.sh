#Shell script to create a docker container and add an interface and corresponding flow in central_ovs

#Create container if it doesn't exist
vm_dup=$(sudo docker ps -a | grep -c $1)
if [[ vm_dup -eq 0 ]]
then
  sudo docker run -t -d --name $1 ubuntu
fi

#Create veth pair and attach it to the central_ovs
sudo ip link add $1_0 type veth peer name $1_1
sudo ip link set $1_0 up
sudo ip link set $1_1 up
pid="$(sudo docker inspect -f '{{.State.Pid}}' "$1")"
sudo mkdir -p /var/run/netns
sudo ln -s /proc/$pid/ns/net /var/run/netns/$1
sudo ip link set $1_1 netns $1
sudo ovs-vsctl add-port central_ovs $1_0

#Find the device
dev=$(sudo ip netns exec ip addr | grep 

#Add an IP address to the interface on container
sudo ip netns exec ip addr add $2 dev $dev

#Add a flow entry in central_ovs with the mac


#Configure VLAN on this port on central_ovs
vm
sudo docker exec -d $1 ip addr
