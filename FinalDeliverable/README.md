## Introduction

The aim of this project was to design and implement a VXLAN solution in a Data Center. The virtualization and management of the infrastructure is also implemented, on top of which the VXLAN tunneling solution is deployed. 

By installing a VXLAN solution, the provider gains the advantage of flexibility in the placement of multi-tenant segments throughout the data center so that L2 segments are extended over the underlying shared L3 infrastructure. In this way, tenant workload can be placed across the physical pods in the data center. 

As a consequence, the mobility of tenant infrastructures (VMs or containers) is also supported. As VMs are booted up, down or moved across the data centre, the network configuration is updated to provide minimally interrupted connection to the VMs.

## Architecture

The following diagram shows the per-physical-pod infrastructure that is created through administrative actions. 

![](HypeTunnel/images/physical_pod.png)

The central_ovs and tunnel_ovs are OVS switches, created and connected whenever a new physical pod is registered to the physical infrastructure. The central_ovs behaves like a normal L2 switch based on L2 Forwarding Table on a per-VLAN basis. The tunnel_ovs is a flow-based switch responsible for tunnel-header encapsulation, decapsulation and forwarding based on the flows configured.

For tenant specific operations, when a new tenant is created, a private tenant router network namespace is created to act as its gateway. When a subnet is added, a veth-pair is connected from the tenant gateway to the central_ovs and the first usable IP address is assigned on the gateway’s interface. This IP will be configured as the default gateway at each of the VMs booted up in this subnet. On the OVS port, an access VLAN will be configured and this VLAN number added as part of trunk VLAN on the port connecting to the tunnel_ovs. Finally, when a VM is created in a subnet, an Ubuntu image is used to spawn a VM and connect a veth-pair from the VM to the central_ovs and an IP address from the pool of usable IP addresses in that subnet is assigned to the VM. On the OVS port, the access VLAN is configured.

## Working - Control Plane 



## Working - Data Plane
### Broadcast Traffic
#### Same physical pod



#### Across physical pods



### Other Traffic
#### Same physical pod



#### Across physical pods



## Screenshots



## Future Scope



## Conclusion
