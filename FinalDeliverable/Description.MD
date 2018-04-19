# Final Deliverable Description
![](https://github.com/kmedidi/HypeTunnel/blob/master/images/FinalDeadline.PNG)

# IDEA
Highly automated system that implements tunneling solution for multi-tenants' VPCs. A Virtual Private Cloud (VPC) of a tenant allows the tenant full freedom on choosing the topology in a virtual world and satisfies the requirements such as connection to the internet, interconnection to certain other tenants and so on. 

# FINAL ARCHITECTURE
![](https://github.com/kmedidi/HypeTunnel/blob/master/images/FinalArchfINAL.png)

# REQUIREMENTS
1. Script 1 - provider_infra.yml - Constructs the above static provider infrastructure of the OVS switches, tunnels and PGW namespaces across all hypervisors.

2. Script 2 - tenant_infra.yml - Creates/ Deletes tenant infrastructure such as L2 bridges, IGWs and VLAN configuration in the OVS switches.

3. Script 3 - tenant_vms.yml - Creates/ Deletes a container for a tenant based on the input from a central JSON file and updates the flows in the OVS switches {Handles VM mobility and Cloud migration}.

4. Script 4 - master_controller - Python/Ansible script that provides the UI and controls and calls all the subordinate scripts according to the user input.

# FILE STRUCTURE
$HOME/HypeTunnel/Scripts - Has all the scripts on remote server only
$HOME/HypeTunnel/Logs - Has logs.txt on remote server only
$HOME/HypeTunnel/Conf - Has flows.txt --> Present on all hypervisors
$HOME/HypeTunnel/Conf - Has database.txt on remote server only

# CONCLUSION
Centralized logging & Configuration Management using Ansible with timestamps incorporates FCAPS model. 
