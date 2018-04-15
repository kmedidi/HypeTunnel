#!/bin/bash
read -p "Enter the number of VMs :" Number
read -p "Enter the Tenant ID :" ID
read -p "Enter the Subnet ID required :" subnet
read -p "Enter the Hypervisor 1's IP address :" Hyp1
read -p "Enter the Hypervisor 2's IP address :" Hyp2
s2="1"
if [ ${#subnet} == 11 ]
then
subnet=${subnet:0:10}${s2:0}
else
subnet=${subnet:0:11}${s2:0}
fi

#Hyp1="$(grep HYP_1 /home/vm1/HypeTunnel/conf/database.txt | awk '{print $3}')"
#Hyp2="$(grep HYP_2 /home/vm1/HypeTunnel/conf/database.txt | awk '{print $3}')"
ThreshMax=20
HalfThresh=$((ThreshMax/2))

###########Function 1: Decide whether the tenant has reached it's full capacity##########
capacity_check (){
echo "Checking the capacity for the Tenant ID "$ID
Capacity=$((ThreshMax - $1))
echo $Capacity
if [ $Number -gt $Capacity ]
then
echo "Cannot provision the requested number..."
echo "Can provision "$Capacity" VMs"
exit 1
fi
}

########### Deciding the required IP address ###########
ip_address_decide (){
IP=$1
TID=$2
s2=1
IP1="TEST"
empty=""
while [ "$IP1" != "$empty" ]
do
IP1=$(grep "T""$TID"" : ""$IP" /home/vm1/HypeTunnel/Scripts/ip_address.log)
    if [ "$IP1" = "" ]
        then
        IP_address=$IP
    fi
s2=$((s2 + 1))
if [ ${#IP} == 11 ]
then
IP=${IP:0:10}$s2
else
IP=${IP:0:11}$s2
fi
done
echo "IP address assigned to the tenant is :"$IP_address
echo "T""$TID" ": "$IP_address >> /home/vm1/HypeTunnel/Scripts/ip_address.log
}
ip_address_decide "$subnet" "$ID"

##########Function 2: Deciding number of VMs on each hypervisor##########################
vm_number_dec (){
echo "Deciding the number of VMs on each hypervisor......"
if [[ $(($1 % 2)) -eq 0 ]]
   then ((VM_Number_Hyp1=$1/2))
   else ((VM_Number_Hyp1=$1/2 + 1))
fi
VM_Number_Hyp2=$(($1 - VM_Number_Hyp1))
echo "Number of VMs on Hypervisor 1 is "$VM_Number_Hyp1
echo "Number of VMs on Hypervisor 2 is "$VM_Number_Hyp2
}
###########Function 3: Decide whether new L2 bridge has to be spawned#####################
if(grep "T"$ID /home/vm1/HypeTunnel/conf/database.txt)
then
VM_Number="$(grep T$ID /home/vm1/HypeTunnel/logs/file.log | awk '{print $6}')"
#No Need to Spawn a New L2 Bridge
#Directly Call Script to Spawn VMs
bridgename="T"$ID"Bridge"
echo $bridgename
capacity_check "$VM_Number"
vm_number_dec "$Number"
exit 1
else
vm_number_dec "$Number"
VM_Number=0
bridgename="T"$ID"Bridge"
#sudo brctl addbr $bridgename
#sudo ip link set bridge up

ssh -T vm1@$Hyp1 -i $HOME/.ssh/proj_key <<EOSSH
#bridgename="T"$ID"Bridge"
sudo brctl addbr $bridgename
sudo ip link set $bridgename up
sudo ip link add vethT$ID type veth peer name ovsT$ID
sudo ip link set vethT$ID up
sudo ip link set ovsT$ID up
sudo brctl addif $bridgename vethT$ID
sudo ovs-vsctl add-port central_ovs ovsT$ID -- set Interface ovsT$ID ofport=$ID
#echo "Bridge Created for $ID with name $bridgename" >> /home/vm1/HypeTunnel/logs/logs.txt
EOSSH
echo $(date) "Bridge created for tenant $ID with name $bridgename on $Hyp1">> /home/vm1/HypeTunnel/logs/logs.txt
ssh -T vm1@$Hyp2 -i $HOME/.ssh/proj_key <<EOSSH
#bridgename="T"$ID"Bridge"
sudo brctl addbr $bridgename
sudo ip link set $bridgename up
sudo ip link add vethT$ID type veth peer name ovsT$ID
sudo ip link set vethT$ID up
sudo ip link set ovsT$ID up
sudo brctl addif $bridgename vethT$ID
sudo ovs-vsctl add-port central_ovs ovsT$ID -- set Interface ovsT$ID ofport=$ID
#echo "Bridge Created for $ID with name $bridgename" >> file.log
EOSSH
echo $(date) "Bridge created for tenant $ID with name $bridgename on $Hyp2">> /home/vm1/HypeTunnel/logs/logs.txt
fi
