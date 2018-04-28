#!/bin/sh

############################## SHELL SCRIPT TO DELETE TENANT CONTAINERS/VMS ###################################

TID = $1
C_NAME=$2
#C_IP = $3
#MAC = $4

#State: present/absent
State=$(sudo docker ps -a | grep -c "<\$C_NAME\>")
if [[ $State == 1 ]]
then
  #echo "$C_NAME is present on Hypervisor"
  #Status =$(sudo docker ps -a --format "table {{.Names}}\t{{.Status}}"| grep "\<$VM_NAME\>" | gawk '{{ print $2 }}')
  Status=$(sudo docker inspect -f {{.State.Status}} $C_NAME)
  if [[ $Status == "running" ]]
  then
    #echo "Shutting down $VM_NAME...."
    sudo docker stop $C_NAME > /dev/null
  else if [[ $Status == "paused" ]]
  then
    sudo docker unpause $C_NAME > /dev/null
    sudo docker stop $C_NAME > /dev/null
  fi
  #echo "Removing $C_NAME...."
  sudo docker rm $C_NAME > /dev/null
  State=$(sudo docker ps -a | grep -c "<\$C_NAME\>")
  if [[ $State == 0 ]];then
    #echo "Successfully removed $C_NAME"
    echo "True"
  fi
else
  #echo " Container not present! Enter the correct Container name."
  echo "False"
fi
