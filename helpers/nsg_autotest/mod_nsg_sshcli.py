import os
import time

DEBUG = True

# nsg_cli works for accessing NSG via jumpbox
def nsg_jmp_cmd(sysip, diag_cmd):
    from dotenv import load_dotenv
    from jumpssh import SSHSession
    
    load_dotenv()

    jumpserver_ip = os.getenv("jumpserver_ip")
    jumpserver_port = os.getenv("jumpserver_port")
    jumpserver_username = os.getenv("jumpserver_username")
    jumpserver_password = os.getenv("jumpserver_password")
    #remote_ip = os.getenv("remote_ip")
    remote_ip = sysip
    remote_port = os.getenv("remote_port")
    remote_username = os.getenv("remote_username")
    remote_password = os.getenv("remote_password")

    gateway_session = SSHSession(jumpserver_ip, jumpserver_username, port=jumpserver_port, password=jumpserver_password).open()

    #remote_session = gateway_session.get_remote_session(remote_ip, port=remote_port, username=remote_username, password=remote_password, allow_agent=False, look_for_keys=False)
    remote_session = gateway_session.get_remote_session(remote_ip, port=int(remote_port), username=remote_username, password=remote_password)
    
    # Save result to txt file
    time_str = time.strftime("%Y%m%d-%H%M%S")
    filename = 'nsg_cli.txt'
    #filename = 'nsg_cli_%s.txt' % time_str

    fl = open("/tmp/"+filename, 'w')
    #fl.write(remote_session.get_cmd_output('nsginfo'))
    #fl.write(remote_session.get_cmd_output(diag_cmd))
    try:
        fl.write(remote_session.get_cmd_output(diag_cmd))
    except:
        print("exception on {}".format(diag_cmd))

    fl.close()
    remote_session.close()
    gateway_session.close()

    return filename

# nsg_cli works for accessing NSG via jumpbox
def nsg_jmp_cmds(edge_id, sysip, commands):
    from dotenv import load_dotenv
    from jumpssh import SSHSession
    
    load_dotenv()

    jumpserver_ip = os.getenv("jumpserver_ip")
    jumpserver_port = os.getenv("jumpserver_port")
    jumpserver_username = os.getenv("jumpserver_username")
    jumpserver_password = os.getenv("jumpserver_password")
    #remote_ip = os.getenv("remote_ip")
    remote_ip = sysip
    remote_port = os.getenv("remote_port")
    remote_username = os.getenv("remote_username")
    remote_password = os.getenv("remote_password")

    try:
        gateway_session = SSHSession(jumpserver_ip, jumpserver_username, port=jumpserver_port, password=jumpserver_password).open()
    except:
        return "Failed to connect to the jumpbox"

    #remote_session = gateway_session.get_remote_session(remote_ip, port=remote_port, username=remote_username, password=remote_password, allow_agent=False, look_for_keys=False)
    try:
        remote_session = gateway_session.get_remote_session(remote_ip, port=int(remote_port), username=remote_username, password=remote_password)
    except:
        return "Failed to connect to the NSG"

    # Save result to txt file
    time_str = time.strftime("%Y%m%d-%H%M%S")
    filename = 'nsg_cli_%s.txt' % time_str

    fl = open("/tmp/"+filename, 'w')
    #fl.write(remote_session.get_cmd_output('nsginfo'))

    fl.write("Results of " + edge_id + "( " +sysip + " ) \n\n")
    for cmd in commands:
        print("Executing {}".format( cmd ))
        try:
            fl.write(cmd + "\n\n")
            fl.write("###### Start of " + cmd + " ######\n\n")
            fl.write(remote_session.get_cmd_output(cmd))
            fl.write(cmd + "\n\n")
            fl.write("###### End of " + cmd + " ######\n")
        except:
            print("exception on {}".format(cmd))

    fl.close()

    remote_session.close()
    gateway_session.close()

    return filename


# nsg_cmds works for accessing NSG directly and multiple cmds
def nsg_cmds(edge_id, sysip, diag_cmd):
    import paramiko

    k = paramiko.RSAKey.from_private_key_file("/root/.ssh/gcp_sli_key")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting")
    c.connect( hostname = sysip, port = "893", username = "nuage", password = "telus123")
    
    print("connected")

    output  = "Results of " + edge_id + "( " +sysip + " ) \n\n"

    for command in commands:
        output += command +"\n\n"
        print("Executing {}".format( command ))
        stdin , stdout, stderr = c.exec_command(command)
 
        # output += str(stdout.read())

        for line in stdout:
            output += line

        output += "\n\n\n"

    c.close()

    # Save result to txt file
    #time_str = time.strftime("%Y%m%d-%H%M%S")
    #filename = '/tmp/nsg_cli_%s.txt' % time_str
    filename = 'nsg_cli.txt'

    fl = open("/tmp/" + filename, 'w')
    fl.write(output)
    fl.close()

    return filename

if __name__ == "__main__":
    #commands = [ "ping cisco.com -c 5" ]
    edge_id = "sli_nsgp8_home"
    commands = [  "nuage-bgp-show summary-all", "ovs-appctl vrf/list alubr0", "ping google.com -c 5", ]

    #nsg_jmp_cmd("69.158.11.147", commands[0])
    #nsg_cmds("209.20.39.20", commands)
    nsg_jmp_cmds(edge_id, "209.29.178.54", commands)