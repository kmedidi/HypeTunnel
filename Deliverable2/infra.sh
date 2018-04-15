#Create directories $HOME/HypeTunnel1, $HOME/HypeTunnel1/conf, $HOME/HypeTunnel1/logs
mkdir -p -- $HOME/HypeTunnel1
mkdir -p -- $HOME/HypeTunnel1/conf
mkdir -p -- $HOME/HypeTunnel1/logs

# Create files $HOME/HypeTunnel1/conf/HypeTunnel1_database, $HOME/HypeTunnel1/conf/flows.txt, $HOME/HypeTunnel1/logs/logs.txt
touch -a $HOME/HypeTunnel1/conf/HypeTunnel1_database.txt
touch -a $HOME/HypeTunnel1/conf/flows.txt
touch -a $HOME/HypeTunnel1/logs/logs.txt

# Create central_ovs
if ovs-vsctl show | grep -q central_ovs
then
 echo "OVS bridge central_ovs exists"
else
 ovs-vsctl add-br central_ovs
 # Getting local ip
 my_ip="$(ip route get 1 | awk '{print $NF;exit}')"
 if [[ $my_ip = "192.168.124.229" ]]; then
  ovs-vsctl add-port central_ovs vxlan1 -- set interface vxlan1 ofport_request=10 type=vxlan options:local_ip=192.168.124.229 options:remote_ip=192.168.124.151
  ovs-vsctl add-port central_ovs gre1 -- set interface gre1 ofport_request=11 type=gre options:remote_ip=192.168.124.151
 fi
 if [[ $my_ip = "192.168.124.151" ]]; then
  ovs-vsctl add-port central_ovs vxlan1 -- set interface vxlan1 ofport_request=10 type=vxlan options:local_ip=192.168.124.151 options:remote_ip=192.168.124.229
  ovs-vsctl add-port central_ovs gre1 -- set interface gre1 ofport_request=11 type=gre options:remote_ip=192.168.124.229
 fi
 echo "OVS bridge central_ovs created and VXLAN and GRE interfaces created"
fi
