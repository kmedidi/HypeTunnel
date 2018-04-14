#!/bin/bash
SELF_HYP_IP=$5

# PREPARE THE EXECUTABLE FILE
echo "sudo bash ${HOME}/vm_create.sh $@" >> $HOME/myscript1.sh
chmod +x $HOME/myscript1.sh
scp -o StrictHostKeyChecking=no -i ${KEY_NAME} $HOME/myscript1.sh mark1@$SELF_HYP_IP://home/mark1/myscript.sh
ssh -t -o StrictHostKeyChecking=no mark1@$SELF_HYP_IP -i ${KEY_NAME} /home/mark1/myscript.sh
rm $HOME/myscript1.sh
