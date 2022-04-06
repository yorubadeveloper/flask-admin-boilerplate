# Author:  Linda Tian  2022
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# Updated with import vspk v6
# Get vrss ip from vsd api
from vspk import v6 as vspk
import time
import math
import pandas as pd
import csv


def getVrssIP(username='', password='', api_url='', enterprise='', certificate=None):

    if not username:
        username = 'csproot'
    if not password:
        password = 'csproot'
    if not api_url:
        api_url = 'https://172.16.68.134:8443'
    if not enterprise:
        enterprise = 'csp'
    try:
        session = vspk.NUVSDSession(
            username=username,
            enterprise=enterprise,
            api_url=api_url,
            password=password,
            certificate=certificate
        )

        session.start()
        user = session.user

        pagesize = 100
        vsc_vrss_list = []

        # time_str = time.strftime("%Y%m%d-%H%M%S")
        ts = time.gmtime()

        for vsp in user.vsps.get():
            for vsc in vsp.vscs.get():
                # if vsc.name == 'CLGRABGUNC30':
                print(vsc.name)

                pages = math.ceil(float(vsc.controller_vrs_links.get_count()) / float(pagesize))
                page_num = 0
                while page_num < pages:
                    page_filter = {
                        'page_size': pagesize,
                        'page': page_num
                    }
                    for vrs_link in vsc.controller_vrs_links.get(**page_filter):
                        # print ('--', len(vrs_link.connections),vrs_link.name, vrs_link.connections)
                        nsg_name = vrs_link.name.replace(vsc.name + '-', '')
                        # print ('--', len(vrs_link.connections),nsg_name, vrs_link.connections)
                        datapathUplinkId = ''
                        publicIP = ''
                        privateIP = ''
                        jsonState = ''
                        openflowState = ''
                        dtlsState = ''
                        ipsecDtlsState = ''
                        uplinkConnection = ''
                        if len(vrs_link.connections) > 0:
                            datapathUplinkId = vrs_link.connections[0]['datapathUplinkId']
                            publicIP = vrs_link.connections[0]['publicIP']
                            privateIP = vrs_link.connections[0]['privateIP']
                            jsonState = vrs_link.connections[0]['jsonState']
                            openflowState = vrs_link.connections[0]['openflowState']
                            dtlsState = vrs_link.connections[0]['dtlsState']
                            ipsecDtlsState = vrs_link.connections[0]['ipsecDtlsState']
                            uplinkConnection = vrs_link.connections[0]['uplinkConnection']
                        # print (len(vrs_link.vrss.get()))
                        if vrs_link.vrss.get() is not None:
                            # print (len(vrs_link.vrss.get()))
                            if len(vrs_link.vrss.get()) > 0:
                                for vrs in vrs_link.vrss.get():
                                    vrs_dpid = vrs.description
                                    vrs_name = vrs.name
                                    vrs_ip = vrs.address
                                    vrs_status = vrs.status
                                    # VSD gui shows the uptime as us with vrs.uptime, make change to be readable
                                    vrs_uptimestamp = vrs.uptime
                                    ms = vrs.uptime
                                    # ms, us = divmod(us, 1000)
                                    s, ms = divmod(ms, 1000)
                                    m, s = divmod(s, 60)
                                    h, m = divmod(m, 60)
                                    d, h = divmod(h, 24)

                                    vrs_uptime = str(d) + 'days' + str(h) + 'hours' + str(m) + 'min'
                                    vrs_hypervisorConnectionState = vrs.hypervisor_connection_state
                                    vrs_role = vrs.role
                                    vrs_status = vrs.status
                                    vrs_managementIP = vrs.management_ip

                        vsc_vrss_list.append(
                            [vsc.name, datapathUplinkId,vrs_dpid, publicIP, nsg_name, privateIP, jsonState, openflowState,
                             dtlsState, ipsecDtlsState, uplinkConnection,
                             vrs_status, vrs_uptime, vrs_uptimestamp,
                             vrs_role, vrs_status, vrs_hypervisorConnectionState, vrs_managementIP,])

                    page_num += 1

        for i in vsc_vrss_list:
            print (i)

        header = ['VSC', 'DPID', 'VRS_DPID', 'NSG_IP', 'NSG_NAME', 'PrivateIP', 'jsonState', 'openflowState', 'dtlsStat','ipsecDtlsState', 'uplinkConnection',
                 'VRS_STATUS', 'NSG_UPTIME', 'UP_TIMESTAMP', 'ROLE', 'status', 'hypervisorConnectionState', 'vrs_managementIP']
        ipdf = pd.DataFrame(vsc_vrss_list, columns=header)
        print (ipdf)

        # ######  Commented for test only START ######
        filename = 'vrss-ip.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in vsc_vrss_list:
                spamwriter.writerow(i)
        # ######  Commented for test only END ######

        return ipdf
    except Exception as e:
        print(e)
        return pd.DataFrame()

getVrssIP()






