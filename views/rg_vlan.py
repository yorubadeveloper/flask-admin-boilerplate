# Author:  Linda Tian  2022 March
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# Check NSG RG'Enterprise', 'RG_name', 'RG_ID' , 'Peer1_name', 'Peer1_ID' , 'Peer2_name', 'Peer2_ID' in NUAGE API V5
# Updated with import vspk v6
# Refer structure to Abisola's nsglist module for db portal March 20, 2022
# # MOdified by :  Abisola Akinrinade  2022
# # Email: abisola.akinrinade@telus.com


from vspk import v6 as vspk
import time
import math
import pandas as pd
import csv

def getRgVlanList(username='', password='', api_url='', enterprise='', certificate=None):

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

        # time_str = time.strftime("%Y%m%d-%H%M%S")
        ts = time.gmtime()

        rg_list = []
        for enterprise in user.enterprises.get():
            for rg in enterprise.ns_redundant_gateway_groups.get():
                # print(rg.name, rg.gateway_peer2_name)
                for port in rg.redundant_ports.get():
                    # if port.physical_name == 'port5':
                    vlans = port.vlans.get()
                    for vlan in vlans:
                        # print(enterprise.name, rg.name, rg.id, rg.gateway_peer1_name, rg.gateway_peer1_id,
                        #       rg.gateway_peer2_name, rg.gateway_peer2_id, port.name, port.physical_name, vlan.id,
                        #       vlan.value)
                        rg_list.append([enterprise.name, rg.name, rg.id, rg.gateway_peer1_name, rg.gateway_peer1_id,
                                        rg.gateway_peer2_name, rg.gateway_peer2_id, port.name, port.physical_name,
                                        vlan.id, vlan.value])


        header = ['Enterprise', 'RG_name', 'RG_id', 'Peer1_name', 'Peer1_ID' , 'Peer2_name', 'Peer2_ID', 'name','port physical', 'vlan_id', 'vlan']
        rgdf = pd.DataFrame(rg_list, columns=header)
        print (rgdf)

        # ######  Commented for test only START ######
        # filename = 'rg.csv'
        # with open(filename, 'w', newline='') as csvfile:
        #     spamwriter = csv.writer(csvfile, delimiter=',',
        #                             quotechar=',', quoting=csv.QUOTE_MINIMAL)
        #     spamwriter.writerow(header)
        #     for i in rg_list:
        #         spamwriter.writerow(i)
        # ######  Commented for test only END ######

        return rgdf
    except Exception as e:
        print(e)
        return pd.DataFrame()

getRgVlanList()