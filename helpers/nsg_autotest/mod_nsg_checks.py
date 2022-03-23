#!/usr/bin/python3
'''
 # @ Author: Shengtao Li
 # @ Create Time: 2021-01-29 09:17:14
 # @ Modified by: Sonia Kanal and Linda Tian
 # @ Modified time: 2021-03-08 22:17:24
 # @ Description: This module includes functions which check individual cmd outputs and return simple good/True or bad/False signal
 '''
# file_name = 'nsg_cli_20210228-163019.txt'

def check_ping(cmd, file_name):
    
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:

        contents = f.readlines()
    
        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start+1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to ping: %s" % str(cmd_output))
            return False, None

        for line in cmd_output:
            print (line)
            if ("0%" or "20%") in line:
                return True, None
    
    return False, None


def check_ipsec_seed(cmd, file_name):
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.readlines()
        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start + 1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to check seed: %s" % str(cmd_output))
            return False, None

        seed = []
        for i in cmd_output[::1]:
            if "HMAC_SHA1" in i:
                seed.append(i)

        for line in seed:
            # print (line)
            if "0x" and "AES_128_CBC" in line and "EXPIRED" not in line:
                str_out = 'Checking Good!! Ipsec seed present'
                print(str_out)
                return True, str_out
            else:
                str_out = 'Alert!!! Missing ipsec seed'
                print(str_out)
                return False, str_out


def check_nsginfo(cmd, file_name):
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.readlines()

        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start + 1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to get nsginfo: %s" % str(cmd_output))
            return False, None

        for i in cmd_output[::1]:
            if "productName" in i:
                product = i
                print(product)
                return True, product


def check_controllerless_mode(cmd, file_name):
    import re
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.readlines()

        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start + 1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to check the controllerless mode: %s" % str(cmd_output))
            return False, None

        for i in cmd_output[::1]:
            if "Local DR Mode" in i:

                i_split = i.split(',')

                Last_DR_mode_entry = i_split[1].lstrip()
                Last_DR_mode_exit = i_split[2].lstrip()
                # print (i_split[1].lstrip(),'\n',i_split[2].lstrip())

                if "No" in i_split[0]:
                    str_out = 'Checking Good!! NSG not in controllerless mode\n' + Last_DR_mode_entry + '\n' + Last_DR_mode_exit
                    print(str_out)
                    return True, str_out
                else:
                    str_out = 'Alert!!! NSG in controllerless mode\n' + Last_DR_mode_entry + '\n' + Last_DR_mode_exit
                    print(str_out)
                    return False, str_out


def check_rg_role(cmd, file_name):
    from datetime import datetime
    import re
    configured = []
    current = []
    ports = []
    flap_time = []
    index = 0
    str_out = ''
    Find_flag = 0
    with open("/tmp/" + file_name, 'r') as f:
        # with open(file_name, 'r') as f:
        contents = f.readlines()

        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start + 1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to ping: %s" % str(cmd_output))
            return False, None
        # The below block has been added to fetch the local time on the NSG
        try:

            cmd1_start = contents.index("###### Start of date ######\n")
            cmd1_end = contents.index(("###### End of date ######\n"))
            cmd1_output = contents[cmd1_start + 1:cmd1_end]

        except KeyError:
            cmd1_output = "error"
            print("Error while trying to fetch: %s" % str(cmd1_output))
            return False, None
        nsg_date = str.rstrip(cmd1_output[1])
        date = datetime.strptime(nsg_date, '%a %b  %d %H:%M:%S %Z %Y')
        print("date=", date)

        for i in cmd_output[::1]:
            if "port" in i:
                ports.append(re.findall('port\d+', i))
                # a = re.findall('port\d+',i)
                # ports.append(a[0])
            if "Flap Time" in i:
                # flap_time.append(re.findall('\d+-\d+-\d+\s\d+:\d+:\d+\W+\d+', i))
                flap_time.append(re.findall('\d+-\d+-\d+\s\d+:\d+:\d+', i))
            if "configured" in i:
                i_split = i.split(' ')
                configured.append(i_split)
            elif "current" in i:
                i_split = i.split(' ')
                current.append(i_split)
        # print (ports)

        for x, y in zip(configured, current):
            current_state = y[-1]
            configured_state = x[-1]
            if x[-1] == y[-1]:

                if (date - datetime.strptime(flap_time[index][0], '%Y-%m-%d %H:%M:%S')).total_seconds() < 300:

                    str_out = str_out + ports[index][
                        0] + ': Alert!! Flap occurred less than 5 minutes ago but No RG failoever triggered, mastership status is ' + current_state + 'configured:' + configured_state + 'Last Flap time:' + \
                              flap_time[index][0] + '\n '
                    # print (str_out)
                    Find_flag += 1
                else:
                    str_out = str_out + ports[index][
                        0] + ': Checking good!! No RG failoever triggered, mastership status is ' + current_state + 'configured:' + configured_state + 'Last Flap time:' + \
                              flap_time[index][0] + '\n '
                    # print (str_out)
            else:
                str_out = str_out + ports[index][
                    0] + ': Alert!!! RG failover triggered, mastership changed to ' + current_state + 'configured:' + configured_state + 'Last flap time:' + \
                          flap_time[index][0] + '\n'
                # print(str_out)
                Find_flag += 1
            index += 1
    if Find_flag == 0 and cmd_output == []:
        str_out = "Alert!! No output found, NSG not a part of RG pair"
        print(str_out)
        return False, str_out
    elif Find_flag > 0:
        print(str_out)
        # print("Find_flag > 0 was triggered")
        return False, str_out

    else:
        print(str_out)
        # print("Find_flag = 0 was triggered")
        return True, str_out

def dump_rg_role(cmd, file_name):
    import re
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.readlines()

        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start + 1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to pinfetch RG role: %s" % str(cmd_output))
            return False, None

    RG_role = []
    str_out = ''
    flag = 0
    for i in cmd_output[::1]:

        if "Access" in i:
            # if "master" or "backup in i" //This also shows access ports with n/a
            if "n/a" not in i:
                flag += 1
                i_split = i.split(" ")
                # print (i_split)
                # RG_role.append(i_split[0]+':'+i_split[-1])
                str_out = str_out + i_split[0] + ': ' + i_split[-1]
    if flag == 0:
        str_out = "NSG not a part of RG pair for any port"
        print(str_out)
        return False, str_out
    else:
        print(str_out)
        return True, str_out


def check_bgp_summary(cmd, file_name):
    import re
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.read()

        try:
            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start+1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to collect bgp summary: %s" % str(cmd_output))
            return False, None

        Find_flag = 0
        str_out = ''
        data = cmd_output
        # Test if No Matching Entries Found return data, can remove later
        if 'No Matching Entries Found' in cmd_output:
            Find_flag = Find_flag + 1
            str_out = cmd_output

        else:
            # Check bgp command output here
            Def_Instance = cmd_output.split('\n')
            # print (len(Def_Instance), type (Def_Instance), '--')
            for i in Def_Instance:
                if 'Def. Instance' in i:
                    # Find   'Connect'   'OpenSent'   'Active'   or 'Idle' set  flag  True
                    if 'Connect' in i or 'OpenSent' in i or 'Active' in i or 'Idle' in i:
                        str_out = Def_Instance[Def_Instance.index(i)-1]+' ' + i +Def_Instance[Def_Instance.index(i)+1]
                        str_out = str_out.replace('           ', ' ')
                        Find_flag = Find_flag + 1

            peer_ip = re.findall('(\d+.\d+.\d+.\d+)\nSvc: ',data)

            # Get Bgp Peer IP
            svc = re.findall('Svc: (.*)', data)
            bold = re.compile(r'\s{1,}')
            index_peer_ip = 0
            for i in svc:
                v = []
                v = bold.split(i)
                Peer_ip = peer_ip[index_peer_ip]  # not all same, save in list
                Route = v[5]

                # match Rcv/Act/Sent
                t = Route.split('/')
                if len(t) != 1:
                    Rcv_route = t[0]
                    Act_route = t[1]
                    Sent_route = t[2]

                    # rec and ack >0, sent =0 Fail
                    if int(Rcv_route)>0 and int(Act_route) >0 and int(Sent_route)==0:
                        Find_flag = Find_flag + 1
                        str_out = str_out + Peer_ip + ' Svc:' + i + '\n'

                else:
                    #if Route == 'Connect' or Route == 'OpenSent' or Route == 'Active' or Route == 'Idle':
                    Find_flag = Find_flag +1
                    str_out = str_out + Peer_ip+' Svc:'+i +'\n'

                index_peer_ip += 1

    if Find_flag == 0:
        str_out = 'BGP checking Good!!!'
    else:
        str_out = 'BGP Alert!!! \n'+ str_out
        print (str_out)

    if Find_flag > 0 : # This including all svc bgp route
        return False, str_out
    else:
        return True, str_out

def check_controller(cmd, file_name):
    import re
    str_out = ''
    alert_flag = 0
    list_controller_error_flag = False
    controller_timer = 300
    Find_flag = 0
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.read()
        try:

            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start+1:cmd_end]

        except KeyError:
            cmd_output = "error"
            print("Error while trying to check controller: %s" % str(cmd_output))
            return False, None

        data_split = cmd_output.split('\n')
        for i in data_split:

            if 'status' in i and '_status' not in i:
                alert_flag = 0
                a = i.replace('sec_since', 'Hour_since')
                # Find all numbers in seconds, replace with hours
                # Save found numbers in seconds in a list to be replace with hours
                seconds_list = re.findall(r'[0-9]+', a)
                # If connect since < 300 S, send alert
                if int(seconds_list[0]) < controller_timer:
                    Find_flag += 1
                    alert_flag = 1
                for j in range(len(seconds_list)):
                    # controller_timer =300s  is for sec_since_connect  sec_since_disconnec? ->fail
                    hours = float(seconds_list[j])/3600
                    hours_decimal = '%.1f' % hours
                    a = a.replace(seconds_list[j], str(hours_decimal))

                if 'state=ACTIVE' not in a:
                    Find_flag += 1
                    alert_flag = 1

                if alert_flag == 1:
                    str_out += 'Alert!!! '
                else:
                    str_out += 'Good!!! '

                str_out += data_split[data_split.index(i)+1]+' '
                str_out += a

                str_out += '\n'

        if Find_flag == 0:
            list_controller_error_flag = False
        else:
            list_controller_error_flag = True

        if list_controller_error_flag == True:
            str_out = 'Controller CONNECTION Alert!!! \n'+ str_out
            print (str_out)
            return False, str_out
        else:
            str_out = 'List Controller checking All Good!!!\n'+ str_out  # All ACTIVE
            print (str_out)
            return True, str_out

def check_vrf_alubr0(cmd, file_name):
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.readlines()
        try:
            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######"))
            cmd_output = contents[cmd_start + 1:cmd_end]
        except KeyError:
            cmd_output = "error"
            print("Error while trying to get VRF: %s" % str(cmd_output))
            return False, None

        data_vrf = cmd_output
        for data in data_vrf:
            if len(data) > 1:
                checking_vrf_info = [int(s) for s in data.split() if s.isdigit()]
                print ( checking_vrf_info)
                if len (checking_vrf_info) == 0:
                    Status = False
                else:
                    Status = True

        if Status == False:
            str_out = 'Alert!!! Missing VRF!!!\n' + data
            print (str_out)
            return False, str_out
        else:
            str_out = 'Good!!! VRF checking!!!\n' + data
            print (str_out)
            return True, str_out

def check_xfrm(cmd, file_name):
    with open("/tmp/" + file_name, 'r') as f:
    # with open(file_name, 'r') as f:
        contents = f.readlines()
        try:
            cmd_start = contents.index("###### Start of " + cmd + " ######\n")
            cmd_end = contents.index(("###### End of " + cmd + " ######\n"))
            cmd_output = contents[cmd_start + 1:cmd_end]
        except KeyError:
            cmd_output = "error"
            print("Error while trying to get xfrm counter: %s" % str(cmd_output))
            return False, None
        str_out = ''
        Status = True
        Find_flag = 0
        XfrmInNoStates = ''
        XfrmOutNoStates =''

        data = cmd_output
        # data_split = data.split('\n')
        for i in data:
            if 'XfrmInNoStates' in i:
                Find_flag += 1
                XfrmInNoStates = i.replace('XfrmInNoStates', '')
                XfrmInNoStates = XfrmInNoStates.replace(' ', '')
                if int(XfrmInNoStates) >0 :
                    Status = False
                    str_out += 'XfrmInNoStates is '+ XfrmInNoStates + ',  '

            if 'XfrmOutNoStates' in i:
                Find_flag += 1
                XfrmOutNoStates = i.replace('XfrmOutNoStates', '')
                XfrmOutNoStates = XfrmOutNoStates.replace(' ', '')
                if int(XfrmOutNoStates) > 0:
                    Status = False
                    str_out += 'XfrmOutNoStates is ' +  XfrmOutNoStates

        if Find_flag ==0 :
            str_out = 'Alert!!! XfrmCounter Missing!!!\n' + str_out
            print (str_out)
            return False, str_out, XfrmInNoStates, XfrmOutNoStates
        if Status == False:
            str_out = 'Alert!!! XfrmCounter Checking!!!\n' + str_out
            print (str_out)
            return False, str_out, XfrmInNoStates, XfrmOutNoStates
        else:
            str_out = 'Good!!! XfrmCounter checking!!!\n' + str_out
            print (str_out)
            return True, str_out, XfrmInNoStates, XfrmOutNoStates

# check_ping('ping google.com -c 5', 'nsg_cli_20210228-163019.txt')
# check_ipsec_seed('ovs-appctl ipsec/list-sa', 'nsg_cli_20210228-163019.txt')
# check_nsginfo('nsginfo', 'nsg_cli_20210228-163019.txt')
# check_controllerless_mode('ovs-appctl ipsec/list-policies', 'nsg_cli_20210228-163019.txt')
# check_rg_role('ovs-appctl bfd/show', 'nsg_cli_20210228-163019.txt')
# dump_rg_role('ovs-ofctl dump-rgs', 'nsg_cli_20210228-163019.txt')
# check_bgp_summary('nuage-bgp-show summary-all', 'nsg_cli_20210228-163019.txt')
# check_controller('sudo ovs-vsctl list c', 'nsg_cli_20210228-163019.txt')
# check_vrf_alubr0('ovs-appctl vrf/list alubr0', 'nsg_cli_20210228-163019.txt')
# check_xfrm('cat /proc/net/xfrm_stat', 'nsg_cli_20210228-163019.txt')

