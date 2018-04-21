import os

#*********************************************************************************************************************************************************
#
# Source: https://gist.github.com/mattyjones/10666342
#

def ssh_command (user, host, password, command):
    """This runs a command on the remote host."""

    print " I am logging into", host

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

def infra():
    '''Function that calls infra.sh to created basic infra'''
    hyplistfile = "hyplistfile.txt"
    with open(hyplistfile, mode = 'rb') as f:
        hypervisors = f.read().split('\n');
        hypMatrix = [{"ip":hypervisors[x].split("*")[0],"uname":hypervisors[x].split("*")[1], "pwd":hypervisors[x].split("*")[2]} for x in range(hypervisors)]
        i = 0
    for hypervisor in hypervisors:
        # Send the shell script to the remote hypervisor
        remote_ip_list = ""
        for hyp in hypervisors:
            if hyp != hypervisor:
                remote_ip_list += str(hyp)
        run_command = "$HOME/HypeTunnel/Conf/infra.sh " + hypMatrix[i]['ip'] + " " + remote_ip_list
        child = ssh_command(hypMatrix[i]['uname'],hypMatrix[i]['ip'],hypMatrix[i]['pwd'],run_command)
        child.expect(pexpect.EOF)
        #output = child.before

    success = True
    return success

#*********************************************************************************************************************************************************

def tenant_infra():
    '''Function that calls tenant_infra.sh to create the infra per hypervisor'''
    success = True
    return success

#*********************************************************************************************************************************************************

def tenant_addvms(tenant):
    '''Function that calls add_vms.sh to create VMs in a specific subnet for a tenant'''
    success = True
    return success

#*********************************************************************************************************************************************************

def tenant_delvms(tenant):
    '''Function that calls del_vms.sh to delete VMs of a specific IP address for a tenant'''
    success = True
    return success

#*********************************************************************************************************************************************************

def database_info():
    '''Function that displays the database file after a password verification'''

#*********************************************************************************************************************************************************

def download_tenant_logs():
    '''Function that reads the log file and creates tenant specific logs'''

#*********************************************************************************************************************************************************

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
            print "4. Add compute resources for a tenant"
            print "5. Remove compute resources for a tenant"
            print "6. Exit Admin Console"
            admin_input = raw_input("Enter your choice: ")
            if int(admin_input) == 1:
                # Call database_info()
            elif int(admin_input) == 2:
                # Call infra()
            elif int(admin_input) == 3:
                # Call tenant_infra()
            elif int(admin_input) == 4:
                # Call tenant_addvms()
            elif int(admin_input) == 5:
                # Call tenant_delvms()
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
                # Create tenant specific database info
            elif int(tenant_input) == 2:
                # Create a log file specific to tenant
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
