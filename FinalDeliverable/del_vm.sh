
#!/bin/bash

TID = $1
C_NAME=$2
MOVE=$3

#State: present/absent
State=$(sudo docker ps -a | grep -c "<\$C_NAME\>")
if [[ $State == 1 ]]
then
  #echo "$C_NAME is present on Hypervisor"
  #Status =$(sudo docker ps -a --format "table {{.Names}}\t{{.Status}}"| grep "\<$VM_NAME\>" | gawk '{{ print $2 }}')
  if [[ $MOVE == "true" ]]
  then
    sudo docker commit $C_NAME ${C_NAME}_Image
    sudo docker save ${C_NAME}_Image >  $HOME/${C_NAME}_Image.tar
    file="$HOME/${C_NAME}_Image.tar"
    if [ -f $file ];then
      echo "True"
    else
      ###Image tar not created###
      echo "False"
    fi
  else
    Status=$(sudo docker inspect -f {{.State.Status}} $C_NAME)
    if [[ $Status == "running" ]]
    then
      #echo "Shutting down $VM_NAME...."
      sudo docker stop $C_NAME
    else if [[ $Status == "paused" ]]
    then
      sudo docker unpause $C_NAME
      sudo docker stop $C_NAME
    fi
    #echo "Removing $C_NAME...."
    sudo docker rm $C_NAME
    State=$(sudo docker ps -a | grep -c "<\$C_NAME\>")
    if [[ $State == 0 ]];then
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
