# HypeTunnel
Semester-long project that aims at creating a highly automated software solution to the tunnel creation problem in the cloud.

# Introduction
An overlay network is a virtual interconnection of nodes over a physical underlay network. The operation of either network is oblivious to the other and is established by intelligent end-points that operate in both of them. The part of the overlay network between these end points is called a tunnel. An overlay network itself is a virtualization concept. In a virtual network world, the underlay network is also implemented in a virtual manner while the overlay network can be thought to exist on a higher level of virtualization.

A Hypervisor Overlay network is one where the tunnel end points are in the Hypervisor of the Host machine. The Underlay network is composed of the actual paths between the participating host and guest machines. Overlay networks provide security, allow operation in a manner determined by the tenant’s administration and separation of concerns. The need for overlay networks in a virtual world which already provides these features is to allow transfer of flexibility to the tenant’s administration in deciding the infrastructure of the network from the virtual network service provider.

# Architecture
The proposed system has the following architecture
![](https://github.com/kmedidi/HypeTunnel/blob/master/images/FinalArch.png)

The proposed architecture assumes a Virtual Private Cloud (VPC) environment set up on a single hypervisor or multiple hypervisors as shown in the diagram. The VPC is assumed to host network devices (like the L3 switches shown in the diagram) and tenant/customer virtual machines (VMs). We use a controller based solution to create overlays because of its advantages like high degree of programmability and ease of maintenance. One SDN controller would suffice in this case but due to redundancy and failure tolerance, we include two SDN controllers - a primary and secondary. Each controller is housed on a separate VPC which in turn houses them on two different hypervisors, possibly on two different physical servers. These controllers assume the control plane tasks of creating overlays and maintaining the forwarding tables appropriately. At any given moment, only one controller is assumed to be the “active” controller while the other remains in a passive state, waiting to take over control if the active controller goes offline due to a fault or failure. So, to enable communication between these controllers and all other network devices, we use an overlay (shown in green) to tunnel the management traffic packets which flow between all hypervisors that are a part of our VPC environment.

Next, our design assumes multi-tenancy and isolation which implies that customer VMs can be created in any hypervisor which contains an overlay compatible network device (like the L3 Switch shown). The design presumes multiple VMs connected to the same virtual switch that belong to the same customer or different customers. This multi tenancy is enabled by creating unique overlays for each customer that is a part of our network. For example, the red and blue tunnels shown in the diagram reflect two customers, one shown in red and the other in blue respectively. These overlays are created from each switch to every other switch in the topology that is connected to one or more of the customer’s VMs. 

Creating these overlays and managing the forwarding tables at each switch is the responsibility of the primary SDN controller. It is also the job of the SDN controller to manage changes in control plane that may be required due to a new customer’s VM creation or mobility.

# Proposed Features
This section gives a brief description about the key features that are offered with our product. We will outline the objective that we aim to accomplish without delving much into the core implementation of the features themselves.

# 1. Highly Automated Solution
Our system plans to provide a simple configuration utility that performs the tasks of enlisting all the selected compute resources onto the overlay network, enabling remote controller flow calculation and pushing these flows into the corresponding virtual switches. The deliverable to the intended consumer of our product is in the form of scripts. Further, these scripts define specific functions that the consumer might want to execute on the system and shall be implemented using the construct of roles of a singular master script. For example, Ansible-Playbook roles.  Some of these tasks have been listed in the following subsection.

The proposed architecture with an SDN Controller offers substantial savings in Network administrator’s time as this is a centralized approach and since the dissemination of information has been automated. Since the Network Controller is defined in software, the Administrator may further reduce effort by using APIs to interact with the network’s devices.

# 1.1 System Management
The major components of any usable product, software or hardware, includes the setup, maintenance and management. These components have a high level of automation with respect to our system.

# 1.1.1 System initial configuration: 
Adhering to a modular approach, our system when deployed on a VPC, allows quick and easy configuration of the required overlay tunnels in the form of a single call to a script that performs all the underlying tasks, given the tenant information.

# 1.1.2 System Management: 
Once the system has been stabilised, the cloud service provider might need to add, delete or modify a tunnel based on the ever-dynamic nature of the cloud and tenant requests. This will also be handled using a specific role for a script. In case of a tenant wanting to augment or change the overlay setup, our system plans to operate on inputs that are understandable to the tenant.

# 1.1.3 System Maintenance: 
The virtual environment is an unreliable and constantly changing system. There are possibilities that end hosts or edge devices having problems or completely failing. In such a case, our system provides reliability in that it can adapt to these changes and account them

# 2. Isolation between tenants
Isolation is a primary goal to be achieved in multi-tenancy. In overlay-based virtual networking, isolation is realized by encapsulating an Ethernet frame received from a VM that is destined to another VM belonging to the same tenancy. Isolation aims at providing communication solely within the tenant machines and hence preventing tenants to get packets from it’s peers on the VPC.

To achieve isolation, various encapsulation schemes (or overlay schemes) can be used, some of the commonly used solutions are Virtual Extended Local Area Network(VXLAN), Generic Routing Encapsulation (GRE), and Stateless Transport Tunneling (STT). Since isolation is an implicit feature of any VPC network, our hypervisor solution will provide support for the same.

# 3. VM Mobility
Virtual machine (VM) mobility is a virtualization feature that enables you to move a VM from one physical host to another. There are two different mechanisms we can use to move VMs around a virtualized environment: hot VM mobility where a running VM is moved from one hypervisor host to another and cold VM mobility where a VM is shut down, and its configuration moved to another hypervisor, where the VM is restarted. 

Hot VM mobility is used by automatic resource schedulers that move running VMs between hypervisors in a cluster to optimize their resource (CPU, RAM) utilization. It is also heavily used for maintenance purposes: for example, you have to evacuate a rack of servers before shutting it down for maintenance or upgrade. On the other hand, cold VM mobility is employed in almost every high-availability (ex: VMware HA restarts a VM after the server failure) and disaster recovery solution. Regardless of its implementation, VM Mobility proves to be an indispensable element in any modern data center environment and hence is inherently one of our features.

# 4. Cloud Migration
Many organizations embark on cloud migrations to achieve scalability, cost-efficiency and higher application performance. But migrating apps to the cloud is a complex process that requires careful planning and deliberation. We aim to provide this feature which gives the ability to scale infrastructure according to the customer’s needs. With this feature we also  provide manageability of the cloud migration as a feature to the provider.

# 5. FCAPS Guarantees
It is imperative for any service provider to place significant emphasis on the quality of the services provided apart from the amount of features offered to appeal to their clientele. In this regards, our overlay solution plans to incorporate the FCAPS model of network management and aims to provide certain guarantees of performance in the features offered to the customer.

One of ways the performance of the system can be ascertained is by the way we approach automating some of the menial and recurring administrative tasks during the deployment phase. Tasks such as creating the required tunnels or updating the networking devices with static route information can be executed prior to customer use. This not only decreases the manual effort from the service provider side but also serves to improve customer experience.

Further, we plan to ease process of administration and accounting of resources (VMs and other Network devices) by generating logs that contain the state information of the each and every resource in the network. Our product also intends to make the network administrator aware of problems by logging faults that occur in the network such as in the event of a VM crash and allowing appropriate action to be taken.

# Conclusion
The document gives description about selected existing solutions offered in the industry and we delve into the architecture that we propose for our product, we then outline some features that we intend to offer in our solution. Finally we’ve given a tentative timeline that has been estimated for each milestone.
