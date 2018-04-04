# Deliverable 2 Description
![](https://github.com/kmedidi/HypeTunnel/blob/master/images/Deadline.PNG)

# Overall Requirements 
Static configuration for multipoint to multipoint L2 VXLAN & L3 GRE tunnels between Tenants' VMs spread across multiple Hypervisors separated across an underlay network (preferrably Internet). All proposed features must be supported

# Architecture
![](https://github.com/kmedidi/HypeTunnel/blob/master/images/arch.png)

# Detailed Requirements
1. Script 1 - Goal: Create a Tenant's VPC on a Hypervisor (Will be run on different hypervisors to establish the infrastructure for this project).

2. Script 2 -  Goal: Based on the input from the Service Provider (Infrastructure owner), CREATE, DELETE & UPDATE a L3 tunnel between the resource locations Public Gateway (PGW) to PGW

3. Script 3 - Goal: Based on Tenant requirement CREATE, DELETE & UPDATE L2 VXLAN tunnels (Switch to Switch)

4. Script 4 - Goal: Based on Tenant requirement CREATE, DELETE & UPDATE L3 GRE tunnels {Internal Gateway (IGW) to IGW}

5. Script 5 -  Goal: Based on trigger from Service Provider/ Tenant about VM migration, proactively update F.T of all VTEPs.

6. Script 6: Goal: Based on input from Service Provider call Scripts 2, 3, 4 & 5 to support migration to cloud.

7. Extra Goal: Currently we will be utilizing the multicast based dynamic address learning at VTEPs. However, a simple goal at Script 2 is to proactively populate VTEP F.T. since all the information is available in one form or the other to our HypeTunnel software.

# Future Scope
Automation of the solution
