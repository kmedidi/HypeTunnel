
#!/bin/bash
##################  SHELL SCRIPT TO DELETE TENANT CONTAINERS/VMs ON THE SPECIFIED HYPERVISOR  ########################

TID=$1
C_NAME=$2
MOVE=$3

echo "INSIDE DEL_VM"
#State: present/absent
State=$(sudo docker ps -a | grep -c "\<$C_NAME\>")
if [[ $State == 1 ]]
then
  echo "del_vm: $C_NAME is present on Hypervisor"
  #Status =$(sudo docker ps -a --format "table {{.Names}}\t{{.Status}}"| grep "\<$VM_NAME\>" | gawk '{{ print $2 }}')
  if [[ $MOVE == "true" ]]
  then
    echo " del_vm: Inside del_vm MOVE block!!!"
    cont=$(echo "$C_NAME" | tr '[:upper:]' '[:lower:]')
    sudo docker commit $C_NAME ${cont}_image
    sudo docker save ${cont}_image >  $HOME/${cont}_image.tar
    file="$HOME/${cont}_image.tar"
    if [ -f $file ]
    then
    echo "del_vm: True MOVED"
    else
      ###Image tar not created###
      echo "del_vm: False MOVED"
    fi
  else
    Status=$(sudo docker inspect -f {{.State.Status}} $C_NAME)
    if [[ $Status == "running" ]]
    then
      #echo "Shutting down $VM_NAME...."
      sudo docker stop $C_NAME
    elif [[ $Status == "paused" ]]
    then
      sudo docker unpause $C_NAME
      sudo docker stop $C_NAME
    fi
    #removing any moved container images
    cont=$(echo "$C_NAME" | tr '[:upper:]' '[:lower:]')
    IMG=$(sudo docker images | grep -c "\<${cont}_image\>")
    if [[ $IMG == 1 ]]
    then
      sudo docker rmi ${cont}_image > /dev/null
    fi
    file="$HOME/${cont}_image.tar"
    if [ -f $file ]
    then
      rm $file
    fi
    #echo "Removing $C_NAME...."
    sudo docker rm $C_NAME > /dev/null
    sudo ovs-vsctl del-port central_ovs ${C_NAME}_0
    State=$(sudo docker ps -a | grep -c "<\$C_NAME\>")
    if [[ $State == 0 ]]
    then
      #echo "Successfully removed $C_NAME"
      echo "True"
    else
      ###Container not removed###
      echo "False"
    fi
  fi
else
    #echo " Container not present! Enter the correct Container name."
    echo "False"
fi





