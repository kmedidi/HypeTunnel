#Create directories $HOME/HypeTunnel, $HOME/HypeTunnel/conf, $HOME/HypeTunnel/logs
sudo mkdir -p -- $HOME/HypeTunnel/conf
sudo mkdir -p -- $HOME/HypeTunnel/logs

# Create files $HOME/HypeTunnel/conf/flows.txt, $HOME/HypeTunnel/logs/logs.txt
sudo touch -a $HOME/HypeTunnel/conf/flows.txt
sudo touch -a $HOME/HypeTunnel/logs/logs.txt

# Create central_ovs if absent
c_present = sudo ovs-vsctl show | grep -c central_ovs
if [[ $c_present -gt 0 ]] then
sudo ovs-vsctl add-br central_ovs
fi

# Create tunnel_ovs if absent
t_present = sudo ovs-vsctl show | grep -c tunnel_ovs
if [[ $t_present -gt 0 ]] then
sudo ovs-vsctl add-br tunnel_ovs
fi

# Getting local ip
my_ip=$1

# Create VXLAN & GRE tunnel interfaces
i=1
for var in "$@"
do
  if ! [[ $i -lt 2 ]]; then
    i_present = sudo ovs-vsctl show | grep -c $i
    if [[ $i_present -gt 0 ]];then
      vxlan_int_name = $i
      gre_int_name = $i + 1
      vxlan_int = $i + 10
      gre_int = $i + 11
      ovs-vsctl add-port central_ovs vxlan_$vxlan_int_name -- set interface vxlan_$i ofport_request=$vxlan_int type=vxlan options:local_ip=$my_ip options:remote_ip=$var
      ovs-vsctl add-port central_ovs gre_$gre_int_name -- set interface gre1 ofport_request=$gre_int type=gre options:remote_ip=$var
    fi
  fi
  i=$(($i+1))
done
