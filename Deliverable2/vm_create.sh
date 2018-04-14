#!/bin/bash
TENANTID=$1
VMNAME=$2
NEWIP=$3
TUNNELID=$4
SELF_HYP_IP=$5
KEY_NAME=${HOME}/.ssh/mark1

# Take current time
current_time=$(date)
echo "$current_time : Creating VM .."
echo "$current_time : Creating VM .." >> $HOME/HypeTunnel/logs/logs.txt

# Create VM
virt-clone -n $VMNAME --original base --auto-clone
echo "$current_time : Tenant $TENANTID VM: $VMNAME Created successfully."
echo "$current_time : Tenant $TENANTID VM: $VMNAME Created successfully." >> $HOME/HypeTunnel/logs/logs.txt

# Start VM
virsh start $VMNAME
MAC=$(virsh dumpxml $VMNAME | awk -F\' '/mac address/ {print $2}')
while true
do
    IP=$(grep -B1 $MAC /var/lib/libvirt/dnsmasq/virbr0.status | head -n 1 | awk '{print $2}' | sed -e s/\"//g -e s/,//)
    if [ "$IP" = "" ]
    then
        sleep 1
    else
        break
    fi
done

# Create veth interface 
ip link add veth_$2_a type veth peer name veth_$2_b
echo "$current_time : Veth interface (veth_$2_a/veth_$2_b) created."
echo "$current_time : Veth interface (veth_$2_a/veth_$2_b) created." >> $HOME/HypeTunnel/logs/logs.txt

# Attach interface to VM
virsh attach-interface $VMNAME --type direct veth_$2_a
echo "$current_time : Veth interface (veth_$2_a) attached to VM."
echo "$current_time : Veth interface (veth_$2_a) attached to VM." >> $HOME/HypeTunnel/logs/logs.txt

# Attach interfaace to bridge
brctl addif T$1Bridge veth_$2_b
echo "$current_time : Veth interface (veth_$2_b) attached to bridge T$1Bridge."
echo "$current_time : Veth interface (veth_$2_b) attached to bridge T$1Bridge." >> $HOME/HypeTunnel/logs/logs.txt

# Get the New MAC address of VM
NEWMAC=`virsh domiflist ${VMNAME} | grep veth_${VMNAME}_a | tail -c 18`

# Prepare the new executable file - for new IP assignment
echo "ip addr add $NEWIP dev ens9" >> $HOME/temp_exec.sh 
echo "ip route add default dev ens9" >> $HOME/temp_exec.sh 

# SCP the executable
scp -o StrictHostKeyChecking=no -i ${KEY_NAME} $HOME/temp_exec.sh root@$IP://root/temp_exec.sh

# SSH and assign the IP address to the VM using executable
ssh -o StrictHostKeyChecking=no root@$IP -i ${KEY_NAME} <<-'ENDSSH'
	sh /root/temp_exec.sh
ENDSSH
echo "$current_time : Static IP $NEWIP configured for VM: $VMNAME."
echo "$current_time : Static IP $NEWIP configured for VM: $VMNAME." >> $HOME/HypeTunnel/logs/logs.txt

# Detach the old interface of the VM
virsh detach-interface $VMNAME --type network --mac $MAC

# Update flows in current hypervisor
sed -i '$ d' $HOME/HypeTunnel/conf/flows.txt
echo "table=1,tun_id=$TUNNELID,dl_dst=$NEWMAC,actions=output:$TENANTID" >> $HOME/HypeTunnel/conf/flows.txt
echo "table=1,tun_id=$TUNNELID,arp,nw_dst=$NEWIP,actions=output:$TENANTID" >> $HOME/HypeTunnel/conf/flows.txt
echo "table=1,priority=100,actions=drop" >> $HOME/HypeTunnel/conf/flows.txt
ovs-ofctl del-flows central_ovs
ovs-ofctl add-flows central_ovs $HOME/HypeTunnel/conf/flows.txt
echo "$current_time : Flows configured for VM: $VMNAME in OVS: central_ovs."
echo "$current_time : Flows configured for VM: $VMNAME in OVS: central_ovs." >> $HOME/HypeTunnel/logs/logs.txt

# Update flows in other hypervisors
for var in "$@"
do
	if ! [[ $i -lt 5 ]]; then
		echo "table=1,tun_id=$TUNNELID,arp,nw_dst=$NEWIP,actions=output:10" >> $HOME/temp_other_hyp.txt
		echo "table=1,tun_id=$TUNNELID,dl_dst=$NEWMAC,actions=output:10" >> $HOME/temp_other_hyp.txt 
		scp -o StrictHostKeyChecking=no -i ${KEY_NAME} $HOME/temp_other_hyp.txt vm1@$IP://home/vm1/temp_other_hyp.txt
		ssh -o StrictHostKeyChecking=no vm1@$var -i ${KEY_NAME} <<-'ENDSSH'
			sed -i '$ d' /home/vm1/HypeTunnel/conf/flows.txt
			cat /home/vm1/temp_other_hyp.txt >> /home/vm1/HypeTunnel/conf/flows.txt
			echo "table=1,priority=100,actions=drop" >> /home/vm1/HypeTunnel/conf/flows.txt
			ovs-ofctl del-flows central_ovs
			ovs-ofctl add-flows central_ovs /home/vm1/HypeTunnel/conf/flows.txt
			rm /home/vm1/temp_other_hyp.txt
		ENDSSH
		echo "$current_time : Flows configured for VM: $VMNAME in OVS: central_ovs on Hypervisor ."
		echo "$current_time : Flows configured for VM: $VMNAME in OVS: central_ovs on Hypervisor ." >> $HOME/HypeTunnel/logs/logs.txt
		rm $HOME/temp_other_hyp.txt
	fi  
	i=$(($i+1)) 
done

# Push new VM details into database
echo "HYP_IP:$SELF_HYP_IP,Tenant:$TENANTID,VM_NAME:$VMNAME,VM_IP:$NEWIP,VM_MAC:$NEWMAC" >> $HOME/HypeTunnel/conf/database.txt
rm $HOME/temp_exec.sh
