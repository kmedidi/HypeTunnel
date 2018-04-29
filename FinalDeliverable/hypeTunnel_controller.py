import os
import filecmp
import pexpect
import datetime
import time

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
    print "************************************"
    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(len(hypervisors))]

    ver_commands = []
    ver_commands.append("sudo ovs-vsctl show | grep -c central_ovs")
    ver_commands.append("sudo ovs-vsctl show | grep -c tunnel_ovs")
    i = 0
    success = True

    for hypervisor in hypervisors:
        # Send the shell script to the remote hypervisor
        os.system("sudo scp -i ~/.ssh/proj_key ./infra.sh "+str(hypervisor.split("*")[1])+"@"+str(hypervisor.split("*")[0])+":$HOME/infra.sh")
        remote_ip_list = ""
        for hyp in hypervisors:
            if hyp != hypervisor:
                remote_ip_list += str(hyp.split("*")[0])+" "
        run_command = "bash $HOME/infra.sh " + hypMatrix[i]['ip'] + " " + remote_ip_list
        child = ssh_command(hypMatrix[i]['uname'],hypMatrix[i]['ip'],hypMatrix[i]['pwd'],run_command)
        child.expect(pexpect.EOF)
        os.system("sudo scp -i ~/.ssh/proj_key ./tenant_infra.sh "+str(hypervisor.split("*")[1])+"@"+str(hypervisor.split("*")[0])+":$HOME/tenant_infra.sh")
        os.system("sudo scp -i ~/.ssh/proj_key ./add_subnet.sh "+str(hypervisor.split("*")[1])+"@"+str(hypervisor.split("*")[0])+":$HOME/add_subnet.sh")
        os.system("sudo scp -i ~/.ssh/proj_key ./add_vm.sh "+str(hypervisor.split("*")[1])+"@"+str(hypervisor.split("*")[0])+":$HOME/add_vm.sh")
        os.system("sudo scp -i ~/.ssh/proj_key ./del_vm.sh "+str(hypervisor.split("*")[1])+"@"+str(hypervisor.split("*")[0])+":$HOME/del_vm.sh")
        for ver_command in ver_commands:
            child = ssh_command(hypMatrix[i]['uname'],hypMatrix[i]['ip'],hypMatrix[i]['pwd'],ver_command)
            child.expect(pexpect.EOF)
            output = child.before
            if int(output) <= 0:
                success = False
        i+=1
    return success

#*********************************************************************************************************************************************************

def tenant_infra(tenant, flag, hypervisor, uname, pwd):
    '''Function that calls tenant_infra.sh to create the infra per hypervisor'''
    success = False
    run_command = "sudo bash $HOME/tenant_infra.sh "+tenant+" "+flag
    child = ssh_command(uname,hypervisor,pwd,run_command)
    child.expect(pexpect.EOF)
    output = child.before
    if  output.find('True') != -1:
        success = True
    return success

#*********************************************************************************************************************************************************

def tenant_addsubnet(subnet, tenant, tag, hypervisor, uname, pwd):
    '''Function to a subnet for a tenant in all hypervisors'''
    success = False
    run_command = "sudo bash $HOME/add_subnet.sh "+tenant+" "+subnet+" "+tag
    child = ssh_command(uname,hypervisor,pwd,run_command)
    child.expect(pexpect.EOF)
    output = child.before
    if output.find('True') != -1:
        success = True
    return success

#*********************************************************************************************************************************************************

def tenant_addvm(vm_name, vm_ip, tag, flag, hypervisor, uname, pwd):
    '''Function that calls add_vm.sh to create VMs in a specific subnet for a tenant on a hypervisor'''
    run_command = "sudo bash $HOME/add_vm.sh "+vm_name+" "+vm_ip+" "+tag+" "+flag
    child = ssh_command(uname, hypervisor, pwd, run_command)
    child.expect(pexpect.EOF)
    output = child.before
    output = output.rstrip()
    vm_mac = output[-17:]
    return vm_mac

#*********************************************************************************************************************************************************

def tenant_delvm(vm_name, tenant, flag, hypervisor, uname, pwd):
    '''Function that calls del_vm.sh to delete VMs of a specific vm_name for a tenant on a hypervisor'''
    run_command = "sudo bash $HOME/del_vm.sh "+tenant+" "+vm_name+" "+flag
    child = ssh_command(uname, hypervisor, pwd, run_command)
    child.expect(pexpect.EOF)
    output = child.before
    success = False
    if output == "True":
        success = True
    return success

#*********************************************************************************************************************************************************

def tenant_vm_stats(vm_name, hypervisor, uname, pwd):
    '''Function that calls del_vm.sh to delete VMs of a specific vm_name for a tenant on a hypervisor'''
    run_command = "sudo docker stats --no-stream=true "+vm_name
    child = ssh_command(uname, hypervisor, pwd, run_command)
    child.expect(pexpect.EOF)
    output = child.before
    return output

#*********************************************************************************************************************************************************

def database_info(databasefile):
    '''Function that displays the database file after a password verification'''
    print "****************************************************************************************************************************"
    print "---HYPERVISOR----TENANT-----SUBNET-------------TAG------VM_NAME-----------VM_IP---------------VM_MAC------  "
    with open(databasefile, mode='rb') as fd:
        line = fd.readline()
        while line:
            parts = line.split('*')
            print parts[0]+"  "+parts[1]+"      "+parts[2]+"       "+parts[3]+"        "+parts[4]+"     "+parts[5]+" "+parts[6]
            line = fd.readline()
    print "****************************************************************************************************************************"

#*********************************************************************************************************************************************************

def write_log(log_line):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logfile = dir_path+"/logfile.txt"
    tstamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    with open(logfile, mode='a+') as fl:
        fl.write("\n"+log_line+"------"+tstamp)

#*********************************************************************************************************************************************************

dir_path = os.path.dirname(os.path.realpath(__file__))
hyplistfile = dir_path+"/hyplistfile.txt"
databasefile = dir_path+"/databasefile.txt"
logfile = dir_path+"/logfile.txt"

if os.path.exists(logfile) != True:
    with open(logfile, mode='w+') as fd:
        print "Created the log file..."

if os.path.exists(databasefile) != True:
    with open(databasefile, mode='w+') as fd:
        print "Created the database file..."
        write_log("HYPETUNNEL DATABASE FILE CREATED")

if os.path.exists(hyplistfile) != True:
    with open(hyplistfile, mode='w+') as fh:
        user_ch = 'Y'
        print "Running first time setup"
        while user_ch == 'Y' or user_ch == 'y':
            hyp = raw_input("Enter the hypervisor IP: ")
            uname = raw_input("Enter the username: ")
            pwd = raw_input("Enter the password: ")
            fh.write(hyp+"*"+uname+"*"+pwd+"\n")
            user_ch = raw_input("Do you have more hypervisors?('Y' or 'N'): ")
        write_log("HYPETUNNEL HYPERVISOR LIST FILE CREATED")

user_input = "1"
while int(user_input) != 3:
    print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l"
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "1. Admin login"
    print "2. Tenant login"
    print "3. Exit"
    user_input = raw_input("Enter your choice: ")
    if int(user_input) == 1:
        write_log("Admin Login")
        admin_input = "1"
        while int(admin_input) != 6:
            print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l  --  A D M I N  C O N S O L E"
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            print "1. Database info"
            print "2. Create HypeTunnel infrastructure"
            print "3. Add/Remove a tenant"
            print "4. Add VM on a new or existing subnet for a tenant"
            print "5. Remove VM from existing subnet for a tenant"
            print "6. Move a VM from one hypervisor to the other"
            print "7. Exit Admin Console"
            admin_input = raw_input("Enter your choice: ")
            if int(admin_input) == 1:
                write_log("Database Info retrieved")
                database_info(databasefile)
            elif int(admin_input) == 2:
                write_log("Create HypeTunnel infrastructure called")
                hypervisors = []
                with open(hyplistfile, mode = 'rb') as f:
                    for line in f:
                        hypervisors.append(line.rstrip());
                result = infra(hypervisors)
                if result == True:
                    print "SUCCESS: HypeTunnel Infrastructure is now up"
                    write_log("SUCCESS: HypeTunnel Infrastructure is now up")
                else:
                    print "FAILED: HypeTunnel Infrastructure has not been modified"
                    write_log("FAILED: HypeTunnel Infrastructure has not been modified")
            elif int(admin_input) == 3:
                write_log("Tenant Infra changed")
                hypervisors = []
                with open(hyplistfile, mode = 'rb') as f:
                    for line in f:
                        hypervisors.append(line.rstrip());
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(len(hypervisors))]
                print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l  --  T E N A N T  C R E A T I O N"
                print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                print "1. Add Tenant"
                print "2. Remove Tenant"
                print "3. Exit"
                ten_choice = raw_input("Enter your choice: ")
                if int(ten_choice) == 1:
                    tenantid = 1
                    with open(databasefile, mode = 'rb') as fd:
                        line = fd.readline()
                        while line:
                            parts = line.split('*')
                            if int(filter(str.isdigit, parts[1])) >= tenantid:
                                tenantid = int(filter(str.isdigit, parts[1]))
                            line = fd.readline()
                    tenantid += 1

                    new_subnet = True
                    for hypElement in hypMatrix:
                        success = tenant_infra(str(tenantid), "true", hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                    if success:
                        print "Tenant Base Infra created successfully!"
                        write_log("Tenant "+str(tenantid)+" : Base Infra created")
                        print "Create subnets and VMs for this tenant now"
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
                                        if parts[1] == "T"+str(tenantid):
                                            if parts[2] == subnet:
                                                new_subnet = False
                                        line = fd.readline()
                                if new_subnet:
                                    with open(databasefile, mode = 'rb') as fd:
                                        line = fd.readline()
                                        new_tag = 1
                                        while line:
                                            parts = line.split('*')
                                            tag = int(parts[3])
                                            if tag >= new_tag:
                                                new_tag = tag+1
                                            line = fd.readline()
                                    print "Subnet " + subnet + " doesn't exist. Creating it..."
                                    for hypElement in hypMatrix:
                                        success = tenant_addsubnet(subnet, str(tenantid), str(new_tag), hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                                        if success == False:
                                            break
                                    if not(success):
                                        print "Tenant T"+str(tenantid)+" : Subnet creation FAILED:"+subnet
                                        write_log("Tenant "+str(tenantid)+" : Subnet creation FAILED:"+subnet)
                                        continue
                                    else:
                                        write_log("Tenant "+str(tenantid)+" : Subnet created:"+subnet)
                                vms = raw_input("Enter the number of VMs: ")
                                if int(vms) > 0:
                                    # Logic to call add_vm repeatedly
                                    with open(databasefile, mode = 'rb') as fd:
                                        line = fd.readline()
                                        vm_name_start = 1
                                        vm_ip_start = 2
                                        while line:
                                            parts = line.split('*')
                                            if parts[1] == "T"+str(tenantid):
                                                id = int(parts[4].split('M')[1])
                                                ip = int(parts[5].split('.')[3].split('/')[0])
                                                if id >= vm_name_start:
                                                    vm_name_start = id
                                                if subnet == parts[2] and ip >= vm_ip_start:
                                                    new_tag = parts[3]
                                                    vm_ip_start = ip
                                            line = fd.readline()
                                        vm_name_start+=1
                                        vm_ip_start+=1

                                    i = 0
                                    for vm in range(int(vms)):
                                        if i == Nhyp:
                                            i = 0
                                        vm_name = "T"+str(tenantid)+"_VM"+str(vm_name_start)
                                        vm_ip = subnet.rsplit('.',1)[0]+'.'+str(vm_ip_start)+'/'+mask
                                        vm_name_start+=1
                                        vm_ip_start+=1
                                        vm_mac = tenant_addvm(vm_name, vm_ip, str(new_tag), "false", hypMatrix[i]['ip'], hypMatrix[i]['uname'], hypMatrix[i]['pwd'])
                                        if vm_mac:
                                            database_line = hypMatrix[i]['ip']+"*"+"T"+str(tenantid)+"*"+subnet+"*"+str(new_tag)+"*"+vm_name+"*"+vm_ip+"*"+vm_mac+"\n"
                                            with open(databasefile, mode='a+') as fd:
                                                fd.write(database_line)
                                            write_log("Tenant "+str(tenantid)+" Subnet:"+subnet+" VM created-->VM name:"+vm_name+" VM MAC: "+vm_mac)
                                        i+=1

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
                            success = tenant_infra(str(tenant), "false", hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                        if success:
                            write_log("Tenant "+str(tenant)+" : deletion in process")
                        rem_lines = []
                        with open(databasefile, mode = 'rb') as fd:
                            line = fd.readline()
                            while line:
                                if line.find('T'+str(tenant)):
                                    parts = line.split('*')
                                    hyp = parts[0]
                                    vm_name = parts[4]
                                    for hypElement in hypMatrix:
                                        if hypElement['ip'] == hyp:
                                            success = tenant_delvm(vm_name, str(tenant),"false", hyp, hypElement['uname'], hypElement['pwd'])
                                        if success:
                                            write_log("Tenant: "+str(tenant)+" VM:"+vm_name+" deleted")
                                            write_log(line)
                                            rem_lines.append(line+'\n')
                                line = fd.readline()
                        new_contents = []
                        with open(databasefile) as fd:
                        	contents = fd.readlines()
                        	for content in contents:
                                    for rem_line in rem_lines:
                                        if rem_line != content.strip():
                                            print "rem_line:"+rem_line
                                            print "rem_line"+content
                                            new_contents.append(content)

                        with open(databasefile, mode = 'w') as fd:
                            fd.writelines(new_contents)
                    else:
                        continue
                else:
                    continue

            elif int(admin_input) == 4:
                hypervisors = []
                tenantid = raw_input("Enter the tenant ID for which you want to add VMs: ")
                subnet = raw_input("Enter the subnet on which you want to add these VMs: ")
                write_log("Addition of VM for Tenant:"+str(tenantid)+" on subnet:"+subnet+" attempted")
                mask = subnet.split('/')[1]
                with open(hyplistfile, mode = 'rb') as f:
                    for line in f:
                        hypervisors.append(line.rstrip());
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(len(hypervisors))]
                new_subnet = True
                with open(databasefile, mode = 'rb') as fd:
                    line = fd.readline()
                    vm_name_start = 1
                    while line:
                        parts = line.split('*')
                        if parts[1] == 'T'+str(tenantid):
                            if parts[2] == subnet:
                                new_subnet = False
                        line = fd.readline()
                if new_subnet:
                    with open(databasefile, mode = 'rb') as fd:
                        line = fd.readline()
                        new_tag = 1
                        while line:
                            parts = line.split('*')
                            tag = int(parts[3])
                            if tag >= new_tag:
                                new_tag = tag+1
                            line = fd.readline()
                    print "Subnet " + subnet + " doesn't exist. Creating it..."
                    for hypElement in hypMatrix:
                        success = tenant_addsubnet(subnet, str(tenantid), str(new_tag), hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                        if success == False:
                            break
                        if not(success):
                            print "Tenant T"+str(tenantid)+" : Subnet creation FAILED:"+subnet
                            write_log("Tenant T"+str(tenantid)+" : Subnet creation FAILED:"+subnet)
                            continue
                        else:
                            write_log("Tenant "+str(tenantid)+" : Subnet created:"+subnet)
                vms = raw_input("Enter the number of additional VMs:")
                with open(databasefile, mode = 'rb') as fd:
                    line = fd.readline()
                    vm_name_start = 1
                    vm_ip_start = 2
                    while line:
                        parts = line.split('*')
                        if parts[1] == str(tenantid):
                            id = int(parts[4].split('M')[1])
                            ip = int(parts[5].split('.')[3].split('/')[0])
                            if id >= vm_name_start:
                                vm_name_start = id
                            if subnet == parts[2] and ip >= vm_ip_start:
                                new_tag = parts[3]
                                vm_ip_start = ip
                        line = fd.readline()
                    vm_name_start+=1
                    vm_ip_start+=1

                i = 0
                for vm in range(int(vms)):
                    if i == Nhyp:
                        i = 0
                    vm_name = "T"+str(tenantid)+"_VM"+str(vm_name_start)
                    vm_ip = subnet.rsplit('.',1)[0]+'.'+str(vm_ip_start)+'/'+mask
                    vm_name_start+=1
                    vm_ip_start+=1
                    vm_mac = tenant_addvm(vm_name, vm_ip, str(new_tag), "false", hypMatrix[i]['ip'], hypMatrix[i]['uname'], hypMatrix[i]['pwd'])
                    if vm_mac:
                        database_line = hypMatrix[i]['ip']+"*"+"T"+str(tenantid)+"*"+subnet+"*"+str(new_tag)+"*"+vm_name+"*"+vm_ip+"*"+vm_mac+"\n"
                        write_log("Tenant "+str(tenantid)+" Subnet:"+subnet+" VM created-->VM name:"+vm_name+" VM MAC: "+vm_mac)
                        with open(databasefile, mode='a+') as fd:
                            fd.write(database_line)
                    i+=1

            elif int(admin_input) == 5:
                tenantid = raw_input("Enter the tenant id: ")
                vm_name = raw_input("Enter the VM name: ")
                del_ch = raw_input("Do you want to save this VM image to boot later?: ")
                write_log("VM deletion for Tenant:"+str(tenant)+" VM:"+vm_name+" attempted")
                with open(databasefile, mode = 'rb') as fd:
                    line = fd.readline()
                    while line:
                        parts = line.split('*')
                        if parts[1] == 'T'+str(tenantid) and vm_name == parts[4]:
                            rem_line = line
                            hypervisor = parts[0]
                        line = fd.readline()
                hypervisors = []
                with open(hyplistfile, mode = 'rb') as f:
                    for line in f:
                        hypervisors.append(line.rstrip());
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(len(hypervisors))]
                for hypElement in hypMatrix:
                    if hypElement['ip'] == hypervisor:
                        success = tenant_delvm(vm_name, str(tenantid), "false", hypervisor, hypElement['uname'], hypElement['pwd'])
                if success:
                    new_contents = []
                    with open(databasefile) as fd:
                    	contents = fd.readlines()
                    	for content in contents:
                                for rem_line in rem_lines:
                                    if rem_line != content.strip():
                                        print "rem_line:"+rem_line
                                        print "rem_line"+content
                                        new_contents.append(content)

                    with open(databasefile, mode = 'w') as fd:
                        fd.writelines(new_contents)
                    write_log("Tenant: "+str(tenantid)+" VM:"+vm_name+" deleted")
                    print "VM deleted successfully"
            elif int(admin_input) == 6:
                vm_name = raw_input("Enter the name of the VM you want to move:")
                hypDestination = raw_input("Enter the final destination (hypervisor) of this VM:")
                with open(databasefile, mode = 'rb') as fd:
                    line = fd.readline()
                    while line:
                        parts = line.split('*')
                        if vm_name == parts[4]:
                            tenantid = int(filter(str.isdigit, parts[1]))
                            subnet = parts[2]
                            tag = parts[3]
                            vm_ip = parts[5]
                            hypSource = parts[0]
                            rem_line = line
                        line = fd.readline()
                hypervisors = []
                with open(hyplistfile, mode = 'rb') as f:
                    for line in f:
                        hypervisors.append(line.rstrip());
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(len(hypervisors))]
                for hypElement in hypMatrix:
                    if hypElement['ip'] == hypSource:
                        hypSource_uname = hypElement['uname']
                        hypSource_pwd = hypElement['pwd']
                        success = tenant_delvm(vm_name, str(tenantid), "true", hypSource, hypElement['uname'], hypElement['pwd'])
                if success:
                    write_log("Tenant: "+str(tenantid)+" VM:"+vm_name+" saved")
                    print "VM successfully saved"

                    vm_ip = subnet.rsplit('.',1)[0]+'.'+str(vm_ip_start)+'/'+mask
                    for hypElement in hypMatrix:
                        if hypElement['ip'] == hypDestination:
                            hypDestination_uname = hypElement['uname']
                            scp_command = "scp -i $HOME/.ssh/proj_key $HOME/"+vm_name+"_image.tar "+hypDestination_uname+"@"+hypDestination+":$HOME/"+vm_name+"_image.tar"
                            child = ssh_command(hypSource_uname, hypSource, hypSource_pwd, scp_command)
                            child.expect(pexpect.EOF)
                            output = child.before
                            vm_mac = tenant_addvm(vm_name, vm_ip, str(tag), "true", hypDestination, hypElement['uname'], hypElement['pwd'])
                    if vm_mac:
                        for hypElement in hypMatrix:
                            if hypElement['ip'] == hypSource:
                                success = tenant_delvm(vm_name, str(tenantid), "false", hypSource, hypElement['uname'], hypElement['pwd'])
                        if success:
                            new_contents = []
                            with open(databasefile) as fd:
                            	contents = fd.readlines()
                            	for content in contents:
                                    if rem_line != content.strip():
                                        print "rem_line:"+rem_line
                                        print "rem_line"+content
                                        new_contents.append(content)
                            with open(databasefile, mode = 'w') as fd:
                                fd.writelines(new_contents)
                            database_line = hypMatrix[i]['ip']+"*"+"T"+str(tenantid)+"*"+subnet+"*"+str(tag)+"*"+vm_name+"*"+vm_ip+"*"+vm_mac+"\n"
                            with open(databasefile, mode='a+') as fd:
                                fd.write(database_line)
                            write_log("Tenant "+str(tenantid)+" Subnet:"+subnet+" VM moved-->VM name:"+vm_name+" VM MAC: "+vm_mac)
            elif int(admin_input) == 7:
                break
            else:
                print "Wrong input"
                admin_input = 1
                continue
    elif int(user_input) == 2:
        tenant_input = "1"
        while int(tenant_input) != 3:
            print "H Y P E R V I S O R  O V E R L A Y  N E T W O R K  --  h y p e T u n n e l  --  T E N A N T  C O N S O L E"
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            print "1. Database info"
            print "2. Get usage info of all your VMs"
            print "3. Exit Tenant Console"
            tenant_input = raw_input("Enter your choice: ")
            if int(tenant_input) == 1:
                tenantid = raw_input("Enter the tenant ID: ")
                write_log("Database retrieved Tenant: T"+str(tenantid))
                with open(databasefile, mode='rb') as fd:
                    line = fd.readline()
                    while line:
                        parts = line.split('*')
                        if parts[1] == 'T'+str(tenantid):
                            print "Subnet:"+parts[2]+"   VM Name:"+parts[4]+"   VM IP:"+parts[5]+"   VM MAC:"+parts[6]
                        line = fd.readline()
            elif int(tenant_input) == 2:
                tenantid = raw_input("Enter the tenant ID: ")
                hypervisors = []
                with open(hyplistfile, mode = 'rb') as f:
                    for line in f:
                        hypervisors.append(line.rstrip());
                    Nhyp = len(hypervisors)
                    hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(len(hypervisors))]
                write_log("Usage Stats retrieved Tenant: T"+str(tenantid))
                with open(databasefile, mode='rb') as fd:
                    line = fd.readline()
                    while line:
                        parts = line.split('*')
                        if parts[1] == 'T'+str(tenantid):
                            for hypElement in hypMatrix:
                                if hypElement['ip'] == parts[0]:
                                    print tenant_vm_stats(vm_name, hypElement['ip'], hypElement['uname'], hypElement['pwd'])
                        line = fd.readline()
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
