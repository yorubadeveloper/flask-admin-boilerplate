# Author:  Linda Tian  2022 March
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# Check NSG RG domain zone subnet vport port association in NUAGE API V5
# Updated with import vspk v6
# Refer structure to Abisola's nsglist module for db portal March 20, 2022
# # MOdified by :  Abisola Akinrinade  2022
# # Email: abisola.akinrinade@telus.com


from vspk import v6 as vspk
import time
import math
import pandas as pd
import csv


def getDomainVportList(username='', password='', api_url='', enterprise='', certificate=None):

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

        vport_list = []
        vlan_dict = {}

        pagesize = 100

        for enterprise in user.enterprises.get():
            print ('######################Checking  NSG info ############################', enterprise.name)
            # if enterprise.name == 'TELUS Stores':
            name_filter = "name is '{}'".format(enterprise.name)
            enterprise = user.enterprises.get_first(filter=name_filter)
            pages = math.ceil(float(enterprise.ns_gateways.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }

                for ns_gat_obj in enterprise.ns_gateways.get(**page_filter):
                    ## Get port vlan information
                    for port in ns_gat_obj.ns_ports.get():
                        vlans = port.vlans.get()
                        if len(vlans) != 0:
                            for vlan in port.vlans.get():
                                if vlan.id not in vlan_dict.keys():
                                    vlan_dict[vlan.id] = [ns_gat_obj.id, ns_gat_obj.system_id, ns_gat_obj.name,
                                                          port.name, port.physical_name]
                page_num += 1

            print(  '######################Checking  RG info ############################', enterprise.name)
            for rg in enterprise.ns_redundant_gateway_groups.get():
                ## Get port vlan information
                for port in rg.redundant_ports.get():
                    vlans = port.vlans.get()
                    if len(vlans) != 0:
                        for vlan in port.vlans.get():
                            if vlan.id not in vlan_dict.keys():
                                vlan_dict[vlan.id] = [rg.id, '', rg.name, port.name, port.physical_name]

        print('###################### lOOKING INTO DOMAIN SUBNET ASSOCIATION NOW ############################')

        for enterprise in user.enterprises.get():
            name_filter = "name is '{}'".format(enterprise.name)
            enterprise = user.enterprises.get_first(filter=name_filter)

            pages = math.ceil(float(enterprise.ns_gateways.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }
                if enterprise.domains.get(**page_filter) is not None:
                    for domain in enterprise.domains.get(**page_filter):
                        if domain.zones.get() is not None:
                            for zone in domain.zones.get():
                                page_num_1 = 0
                                pages_1 = math.ceil(float(zone.subnets.get_count()) / float(pagesize))
                                while page_num_1 < pages_1:
                                    page_filter_1 = {
                                        'page_size': pagesize,
                                        'page': page_num_1
                                    }
                                    if zone.subnets.get(**page_filter_1) is not None:
                                        for subnet in zone.subnets.get(**page_filter_1):
                                            if subnet.vports.get() is not None:
                                                for vport in subnet.vports.get():
                                                    if vport.vlanid in vlan_dict.keys():
                                                        vport_list.append(
                                                            [enterprise.name, domain.name, domain.service_id, zone.name,
                                                             subnet.name,
                                                             subnet.gateway, subnet.address, subnet.netmask, vlan.id,
                                                             vport.associated_gateway_id,
                                                             vlan_dict[vport.vlanid][1], vlan_dict[vport.vlanid][2],
                                                             vlan_dict[vport.vlanid][3], vlan_dict[vport.vlanid][4]])
                                    page_num_1 += 1
                page_num += 1

        header = ['Enterprise', 'Domain', 'VPRN', 'Zone', 'Subnet', 'GW_IP', 'Address', 'Netmask', 'vlan_id', 'GW_id',
                  'DPID', 'GW_NAME', 'PORT', 'port_NAME']

        vportdf = pd.DataFrame(vport_list, columns=header)
        print (vportdf)

        # ######  Commented for test only START ######
        # filename = 'Domain_Subnet_NSG_RG.csv'
        # with open(filename, 'w', newline='') as csvfile:
        #     spamwriter = csv.writer(csvfile, delimiter=',',
        #                             quotechar=',', quoting=csv.QUOTE_MINIMAL)
        #     spamwriter.writerow(header)
        #     for i in vport_list:
        #         spamwriter.writerow(i)
        # ######  Commented for test only END ######

        return vportdf
    except Exception as e:
        print(e)
        return pd.DataFrame()

getDomainVportList()