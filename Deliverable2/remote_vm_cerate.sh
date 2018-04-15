#!/bin/bash
# sudo bash <full_path_to_remote_vm_create.sh>/remote_vm_create.sh <TenantID> <VMNAME> <VM_NEWIP> <VXLAN_TUNNELID> <VM_HYPERVISOR_IP> <Other-hypervisor_IP_1> <Other_Hypervisor_IP_2> ...
SELF_HYP_IP=$5

# PREPARE THE EXECUTABLE FILE
echo "sudo bash ${HOME}/vm_create.sh $@" >> $HOME/myscript1.sh
chmod +x $HOME/myscript1.sh
scp -o StrictHostKeyChecking=no -i ${KEY_NAME} $HOME/myscript1.sh mark1@$SELF_HYP_IP://home/mark1/myscript.sh
ssh -t -o StrictHostKeyChecking=no mark1@$SELF_HYP_IP -i ${KEY_NAME} /home/mark1/myscript.sh
rm $HOME/myscript1.sh
