import os
import filecmp
import pexpect

#*********************************************************************************************************************************************************
#
# Source: https://gist.github.com/mattyjones/10666342
#

def ssh_command (user, host, password, command):
    """This runs a command on the remote host."""

    ssh_newkey = 'Are you sure you want to continue connecting'
    child = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    if i == 0: # Timeout
        print('ERROR!')
        print('SSH could not login. Here is what SSH said:')
        print(child.before, child.after)
        return None
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        child.expect ('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            print('9ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print(child.before, child.after)
            return None
    child.sendline(password)
    return child

#*********************************************************************************************************************************************************

def infra(hypervisors):
    '''Function that calls infra.sh to created basic infra'''
    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(hypervisors)]

    ver_commands = []
    ver_commands.append("sudo ovs-vsctl show | grep -c central_ovs")
    ver_commands.append("sudo ovs-vsctl show | grep -c tunnel_ovs")
    ver_commands.append("sudo ovs-vsctl show | grep -c central_ovs")
    i = 0
    success = True
    for hypervisor in hypervisors:
        # Send the shell script to the remote hypervisor
        remote_ip_list = ""
        for hyp in hypervisors:
            if hyp != hypervisor:
                remote_ip_list += str(hyp)+" "
        run_command = "bash $HOME/HypeTunnel/Conf/infra.sh " + hypMatrix[i]['ip'] + " " + remote_ip_list
        child = ssh_command(hypMatrix[i]['uname'],hypMatrix[i]['ip'],hypMatrix[i]['pwd'],run_command)
        child.expect(pexpect.EOF)
        #output = child.before
        for ver_command in ver_commands:
            child = ssh_command(hypMatrix[i]['uname'],hypMatrix[i]['ip'],hypMatrix[i]['pwd'],ver_command)
            child.expect(pexpect.EOF)
            output = child.before
            if int(output) < 0:
                success = False
    return success

#*********************************************************************************************************************************************************

def tenant_infra(tenant, flag, hypervisor, uname, pwd):
    '''Function that calls tenant_infra.sh to create the infra per hypervisor'''
    success = False
    run_command = "sudo bash $HOME/HypeTunnel/Conf/tenant_infra.sh "+tenant+" "+flag
    child = ssh_command(uname,hypervisor,pwd,run_command)
    child.expect(pexpect.EOF)
    output = child.before
    if output == '1':
        success = True
    return success

#*********************************************************************************************************************************************************

def tenant_addsubnet(subnet, tenant, hypervisor, uname, pwd):
    '''Function to a subnet for a tenant in all hypervisors'''
    success = False
    run_command = "sudo bash $HOME/HypeTunnel/Conf/add_subnet.sh "+tenant+" "+subnet
    child = ssh_command(uname,hypervisor,pwd,run_command)
    child.expect(pexpect.EOF)
    output = child.before
    if output == '1':
        success = True
    return success

#*********************************************************************************************************************************************************

def tenant_addvm(vm_name, vm_ip, tenant, hypervisor, uname, pwd):
    '''Function that calls add_vm.sh to create VMs in a specific subnet for a tenant on a hypervisor'''
    run_command = "sudo bash $HOME/HypeTunnel/Conf/add_vm.sh "+vm_name+" "+vm_ip+" "+tenant
    child = ssh_command(uname, hypervisor, pwd, run_command)
    child.expect(pexpect.EOF)
    vm_mac = child.before
    return vm_mac

#*********************************************************************************************************************************************************

def tenant_delvm(vm_name, tenant, hypervisor, uname, pwd):
    '''Function that calls del_vms.sh to delete VMs of a specific vm_name for a tenant on a hypervisor'''
    success = True
    return success

#*********************************************************************************************************************************************************

def database_info():
    '''Function that displays the database file after a password verification'''
    #TODO
#*********************************************************************************************************************************************************

def download_tenant_logs():
    '''Function that reads the log file and creates tenant specific logs'''
    #TODO

#*********************************************************************************************************************************************************

hyplistfile = "hyplistfile.txt"
databasefile = "databasefile.txt"
user_input = "1"
while int(user_input) != 3:
    print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l"
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "1. Admin login"
    print "2. Tenant login"
    print "3. Exit"
    user_input = raw_input("Enter your choice: ")
    if int(user_input) == 1:
        admin_input = "1"
        while int(admin_input) != 6:
            print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l  --  A D M I N  C O N S O L E"
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            print "1. Database info"
            print "2. Create HypeTunnel infrastructure"
            print "3. Add/Remove a tenant"
            print "4. Add compute resource on a new or existing subnet for a tenant"
            print "5. Remove compute resources on a new or existing subnet for a tenant"
            print "6. Exit Admin Console"
            admin_input = raw_input("Enter your choice: ")
            if int(admin_input) == 1:
                # TODO: Call database_info()
            elif int(admin_input) == 2:
                with open(hyplistfile, mode = 'rb') as f:
                    hypervisors = f.read().split('\n');
                result = infra(hypervisors)
                if result == True:
                    print "SUCCESS: HypeTunnel Infrastructure is now up"
                else:
                    print "FAILED: HypeTunnel Infrastructure has not been modified"
            elif int(admin_input) == 3:
                with open(hyplistfile, mode = 'rb') as f:
                    hypervisors = f.read().split('\n');
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(hypervisors)]
                print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l  --  T E N A N T  C O N S O L E"
                print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                print "1. Add Tenant"
                print "2. Remove Tenant"
                print "3. Exit"
                ten_choice = raw_input("Enter your choice: ")
                if int(ten_choice) == 1:
                    # TODO: Logic to create a new tenant id
                    new_subnet = True
                    for hypElement in hypMatrix:
                        success = tenant_infra(tenant, "true", hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                    if sucess:
                        print "Tenant Base Infra created successfully!"
                        print "1. Create subnets and VMs for this tenant now"
                        print "2. Exit & Create subnets later"
                        user_choice = raw_input("Enter your choice: ")
                        if int(user_choice) == 1:
                            subnet = 'a'
                            while subnet != 'X':
                                subnet = raw_input("Enter the subnet ID (Type 'X' to exit): ")
                                if subnet != 'X':
                                    mask = subnet.split('/')[1]
                                    new_subnet = True
                                    with open(databasefile, mode = 'rb') as fd:
                                        line = fd.readline()
                                        vm_name_start = 1
                                        while line:
                                            parts = line.split('*')
                                            if parts[1] == tenantid:
                                                if parts[2] == subnet:
                                                    new_subnet = False
                                    if new_subnet:
                                        print "Subnet " + subnet + " doesn't exist. Creating it..."
                                        for hypElement in hypMatrix:
                                            tenant_addsubnet(subnet, tenantid, hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                                    vms = raw_input("Enter the number of VMs: ")
                                    if int(vms) > 0:
                                        # Logic to call add_vm repeatedly
                                        with open(databasefile, mode = 'rb') as fd:
                                            line = fd.readline()
                                            vm_name_start = 1
                                            vm_ip_start = 2
                                            while line:
                                                parts = line.split('*')
                                                if parts[1] == tenantid:
                                                    id = int(parts[3].split('M')[1])
                                                    ip = int(parts[4].split('.')[3].split('/')[0])
                                                    if id >= vm_name_start:
                                                        vm_name_start = id
                                                    if ip >= vm_ip_start:
                                                        vm_ip_start = ip
                                                line = fd.readline()
                                            vm_name_start++
                                            vm_ip_start++

                                        i = 0
                                        for vm in range(int(vms)):
                                            if i == Nhyp-1:
                                                i = 0
                                            vm_name = "T"+tenantid+"_VM"+str(vm_name_start)
                                            vm_ip = subnet.rsplit('.',1)[0]+str(vm_ip_start)+'/'+mask
                                            vm_name_start++
                                            vm_ip_start++
                                            tenant_addvm(vm_name, vm_ip, tenantid, hypMatrix[i]['ip'], hypMatrix[i]['uname'], hypMatrix[i]['pwd'])
                                            i++
                                        vm_mac = tenant_addvm()
                                        # TODO: Log the vm_mac and add it to database file

                elif int(ten_choice) == 2:
                    # Logic to remove tenant NS and all VMs
                    tenant = raw_input("Enter the tenant ID: ")
                    print "WARNING!!!: Deleting this tenant will remove all VMs for this tenant across all hypervisors"
                    print "Are you sure you want to remove this tenant?"
                    print "1. Yes"
                    print "2. No. Cancel"
                    user_choice = raw_input("Enter your choice: ")
                    if int(user_choice) == 1:
                        # Logic to remove
                        for hypElement in hypMatrix:
                            success = tenant_infra(tenant, "false", hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                        rem_lines = []
                        with open(databasefile, mode = 'rb') as fd:
                            line = fd.readline()
                            if line.find('T'+str(tenant)):
                                parts = line.split('*')
                                hyp = parts[0]
                                vm_name = parts[3]
                                for hypElement in hypMatrix:
                                    if hypElement['ip'] == hyp:
                                        success = tenant_delvm(tenant, vm_name, hyp, hypElement['uname'], hypElement['pwd'])
                                        if success:
                                            rem_lines.append(line+'\n')
                        with open(databasefile, mode = 'rb') as fd:
                            contents = fd.read()
                            for rem_line in rem_lines:
                                contents.replace(rem_line,"")
                        with open(databasefile, mode = 'w') as fd:
                            fd.write(contents)
                    else:
                        continue
                else:
                    continue

            elif int(admin_input) == 4:
                tenantid = raw_input("Enter the tenant ID for which you want to add VMs: ")
                subnet = raw_input("Enter the subnet on which you want to add these VMs: ")
                mask = subnet.split('/')[1]
                with open(hyplistfile, mode = 'rb') as f:
                    hypervisors = f.read().split('\n');
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(hypervisors)]
                new_subnet = True
                with open(databasefile, mode = 'rb') as fd:
                    line = fd.readline()
                    vm_name_start = 1
                    while line:
                        parts = line.split('*')
                        if parts[1] == tenantid:
                            if parts[2] == subnet:
                                new_subnet = False
                if new_subnet:
                    print "Subnet " + subnet + " doesn't exist. Creating it..."
                    for hypElement in hypMatrix:
                        tenant_addsubnet(subnet, tenantid, hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                vms = raw_input("Enter the number of additional VMs:")
                with open(databasefile, mode = 'rb') as fd:
                    line = fd.readline()
                    vm_name_start = 1
                    vm_ip_start = 2
                    while line:
                        parts = line.split('*')
                        if parts[1] == tenantid:
                            id = int(parts[3].split('M')[1])
                            ip = int(parts[4].split('.')[3].split('/')[0])
                            if id >= vm_name_start:
                                vm_name_start = id
                            if ip >= vm_ip_start:
                                vm_ip_start = ip
                        line = fd.readline()
                    vm_name_start++
                    vm_ip_start++

                i = 0
                for vm in range(int(vms)):
                    if i == Nhyp-1:
                        i = 0
                    vm_name = "T"+tenantid+"_VM"+str(vm_name_start)
                    vm_ip = subnet.rsplit('.',1)[0]+str(vm_ip_start)+'/'+mask
                    vm_name_start++
                    vm_ip_start++
                    tenant_addvm(vm_name, vm_ip, tenantid, hypMatrix[i]['ip'], hypMatrix[i]['uname'], hypMatrix[i]['pwd'])
                    i++
                vm_mac = tenant_addvm()
                # TODO: Log the vm_mac and add it to database file

            elif int(admin_input) == 5:
                # TODO: Call tenant_delvms()
            elif int(admin_input) == 6:
                break
            else:
                admin_input = 1
                continue
    elif int(user_input) == 2:
        tenant_input == "1"
        while int(tenant_input) != 3:
            print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l  --  T E N A N T  C O N S O L E"
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            print "1. Database info"
            print "2. Download log files"
            print "3. Exit Tenant Console"
            tenant_input = raw_input("Enter your choice: ")
            if int(tenant_input) == 1:
                # TODO: Create tenant specific database info
            elif int(tenant_input) == 2:
                # TODO: Create a log file specific to tenant
            elif int(tenant_input) == 3:
                break
            else:
                tenant_input = 1
                continue
    elif int(user_input) == 3:
        break
    else:
        user_input = 1
        continue

#*********************************************************************************************************************************************************
