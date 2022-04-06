# Author:  Linda Tian  2022 March
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# Get Domain / zone 1 2 3 for VVAS MPLS BGP policy name/description to get Primary/secondary RE from vsd API
# Updated with import vspk v6
# Refer structure to Abisola's nsglist module for db portal March 20, 2022
# # MOdified by :  Abisola Akinrinade  2022
# # Email: abisola.akinrinade@telus.com

from vspk import v6 as vspk
import time
import math
import pandas as pd
import csv


def getNsgList(username='', password='', api_url='', enterprise='', certificate=None):

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

        LAN_list = []
        bgp_list = []
        vport_list = []
        network_dict = {}
        bgp_policy_dict = {}
        bgp_policy_dict_keys = ''
        bgp_policy_dict_values = []

        page_num = 0
        pagesize = 100
        pagesize_1 = 100

        for enterprise in user.enterprises.get():
            print ('--Getting NSG Info--',enterprise.name)
            # if enterprise.name == 'VIA RAIL CANADA INC':
            pages = math.ceil(float(enterprise.ns_gateways.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }

                for nsg in enterprise.ns_gateways.get(**page_filter):
                    network_dict[nsg.id] = [nsg.system_id, nsg.name]
                    for port in nsg.ns_ports.get():
                        if port.name != "WAN1" and port.name != "WAN2":
                            vlans = port.vlans.get()
                            for vlan in vlans:
                                network_dict[vlan.id] = [vlan.value, port.name, port.physical_name, nsg.name, '', '',
                                                         '', '']
                                LAN_list.append(
                                    [enterprise.name, nsg.id, port.name, port.physical_name, vlan.value, nsg.name, '',
                                     '', '', ''])

                page_num += 1

        for enterprise in user.enterprises.get():
            # if enterprise.name == 'VIA RAIL CANADA INC':
            # Get RG information
            print('--Getting RG Info--', enterprise.name)
            for rg in enterprise.ns_redundant_gateway_groups.get():
                network_dict[rg.id] = rg.name
                # print rg.name, rg.gateway_peer2_name
                # RG_list.append([enterprise.name, rg.name, rg.gateway_peer1_name, network_dict[rg.gateway_peer1_id], rg.gateway_peer2_name, network_dict[rg.gateway_peer2_id]])
                for port in rg.redundant_ports.get():
                    vlans = port.vlans.get()
                    if len(vlans) != 0:
                        for vlan in vlans:
                            # print (rg.gateway_peer1_id, '-----', rg.gateway_peer2_id, '-----')
                            # print (network_dict[rg.gateway_peer1_id], '-----', network_dict[rg.gateway_peer2_id], '-----')
                            # note  network_dict[nsg.id] = [nsg.system_id, nsg.name]
                            if len(vlans) != 0:
                                if rg.gateway_peer1_id in network_dict.keys() and rg.gateway_peer2_id in network_dict.keys():
                                    network_dict[vlan.id] = [vlan.value, port.name, port.physical_name, rg.name,
                                                             network_dict[rg.gateway_peer1_id][1], rg.gateway_peer1_id,
                                                             network_dict[rg.gateway_peer2_id][1], rg.gateway_peer2_id]
                                    LAN_list.append(
                                        [enterprise.name, rg.id, port.name, port.physical_name, vlan.value, rg.name,
                                         network_dict[rg.gateway_peer1_id][1], rg.gateway_peer1_id,
                                         network_dict[rg.gateway_peer2_id][1], rg.gateway_peer2_id])
                                else:
                                    if rg.gateway_peer1_id in network_dict.keys():
                                        print('RG has only 1 peer')
                                        network_dict[vlan.id] = [vlan.value, port.name, port.physical_name, rg.name,
                                                                 network_dict[rg.gateway_peer1_id][1],
                                                                 rg.gateway_peer1_id, '', rg.gateway_peer2_id]

                                        LAN_list.append(
                                            [enterprise.name, rg.id, port.name, port.physical_name, vlan.value, rg.name,
                                             network_dict[rg.gateway_peer1_id][1], rg.gateway_peer1_id, '',
                                             rg.gateway_peer2_id])

                ############ Get routing policy bgp name dictionary ###########
        for enterprise in user.enterprises.get():
            # if enterprise.name == 'VIA RAIL CANADA INC':
            print('--Getting Routing policy--', enterprise.name)
            for routing_policy in enterprise.routing_policies.get():
                # print (routing_policy.name, routing_policy.description, routing_policy.id )
                bgp_policy_dict_keys = routing_policy.id
                bgp_policy_dict_values = [routing_policy.name, routing_policy.description]
                bgp_policy_dict[bgp_policy_dict_keys] = bgp_policy_dict_values
            ############ Get routing policy bgp name dictionary ###########

            pages = math.ceil(float(enterprise.domains.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }

                for domain in enterprise.domains.get(**page_filter):
                    for zone in domain.zones.get():

                        page_num_1 = 0
                        pages_1 = math.ceil(float(zone.subnets.get_count()) / float(pagesize_1))
                        while page_num_1 < pages_1:
                            page_filter_1 = {
                                'page_size': pagesize_1,
                                'page': page_num_1
                            }
                            if len(zone.subnets.get(**page_filter_1)) != 0:
                                for subnet in zone.subnets.get(**page_filter_1):

                                    for bgp_nei in subnet.bgp_neighbors.get():
                                        if bgp_nei != None:
                                            bgp_nei_import_name = ''
                                            bgp_nei_import_desp = ''
                                            bgp_nei_export_name = ''
                                            bgp_nei_export_desp = ''

                                            if bgp_nei.associated_import_routing_policy_id in bgp_policy_dict.keys():
                                                # print(len(bgp_policy_dict[bgp_nei.associated_import_routing_policy_id]), '++++++',type(bgp_policy_dict[bgp_nei.associated_import_routing_policy_id]),bgp_policy_dict[bgp_nei.associated_import_routing_policy_id] )
                                                bgp_nei_import_name = \
                                                bgp_policy_dict[bgp_nei.associated_import_routing_policy_id][0]
                                                bgp_nei_import_desp = \
                                                bgp_policy_dict[bgp_nei.associated_import_routing_policy_id][1]

                                            if bgp_nei.associated_export_routing_policy_id in bgp_policy_dict.keys():
                                                bgp_nei_export_name = \
                                                bgp_policy_dict[bgp_nei.associated_export_routing_policy_id][0]
                                                bgp_nei_export_desp = \
                                                bgp_policy_dict[bgp_nei.associated_export_routing_policy_id][1]

                                            network_dict[subnet.id] = [bgp_nei.name, bgp_nei.peer_as, bgp_nei.peer_ip,
                                                                       bgp_nei.associated_import_routing_policy_id,
                                                                       bgp_nei.associated_export_routing_policy_id,
                                                                       bgp_nei_import_name, bgp_nei_import_desp,
                                                                       bgp_nei_export_name, bgp_nei_export_desp]
                                            bgp_list.append([enterprise.name, domain.name, zone.name, subnet.name,
                                                             domain.service_id, subnet.gateway, subnet.address,
                                                             subnet.netmask, bgp_nei.name, bgp_nei.peer_as,
                                                             bgp_nei.peer_ip,
                                                             bgp_nei.associated_import_routing_policy_id,
                                                             bgp_nei.associated_export_routing_policy_id,
                                                             bgp_nei_import_name, bgp_nei_import_desp,
                                                             bgp_nei_export_name, bgp_nei_export_desp])
                            page_num_1 += 1
                page_num += 1

        for enterprise in user.enterprises.get():
            # if enterprise.name == 'VIA RAIL CANADA INC':
            pages = math.ceil(float(enterprise.domains.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }

                for domain in enterprise.domains.get(**page_filter):
                    for zone in domain.zones.get():
                        # print (domain.name, zone.name)

                        page_num_1 = 0
                        pages_1 = math.ceil(float(zone.subnets.get_count()) / float(pagesize_1))
                        while page_num_1 < pages_1:
                            page_filter_1 = {
                                'page_size': pagesize_1,
                                'page': page_num_1
                            }
                            if len(zone.subnets.get(**page_filter_1)) != 0:
                                for subnet in zone.subnets.get(**page_filter_1):

                                    if len(subnet.vports.get()) != 0:
                                        for vport in subnet.vports.get():
                                            # vport_list.append([enterprise.name, domain.name, zone.name, subnet.name, bgp_nei.name, bgp_nei.peer_ip,
                                            #        bgp_nei.associated_import_routing_policy_id,
                                            #        bgp_nei.associated_export_routing_policy_id,
                                            #        bgp_nei_import_name,bgp_nei_import_desp, bgp_nei_export_name, bgp_nei_export_desp,
                                            #        vport.name, vport.associated_gateway_id,vport.vlan, vport.vlanid, network_dict[vport.vlanid]])
                                            if subnet.id in network_dict.keys() and vport.vlanid in network_dict.keys():
                                                # network_dict[vlan.id] is [vlan.value, port.name, port.physical_name, rg.name, rg.gateway_peer1_name, network_dict[rg.gateway_peer1_id], rg.gateway_peer2_name, network_dict[rg.gateway_peer2_id ]
                                                vport_list.append(
                                                    [enterprise.name, domain.name, zone.name, subnet.name,
                                                     domain.service_id, subnet.gateway, subnet.address, subnet.netmask,
                                                     network_dict[subnet.id][0], network_dict[subnet.id][1],
                                                     network_dict[subnet.id][2], network_dict[subnet.id][3],
                                                     network_dict[subnet.id][4], network_dict[subnet.id][5],
                                                     network_dict[subnet.id][6], network_dict[subnet.id][7],
                                                     network_dict[subnet.id][8],
                                                     vport.name, vport.id, vport.associated_gateway_id, vport.vlan,
                                                     vport.vlanid,
                                                     network_dict[vport.vlanid][1], network_dict[vport.vlanid][2],
                                                     network_dict[vport.vlanid][3],
                                                     network_dict[vport.vlanid][4], network_dict[vport.vlanid][5],
                                                     network_dict[vport.vlanid][6],
                                                     network_dict[vport.vlanid][7]])
                                            else:
                                                if subnet.id in network_dict.keys() and vport.vlanid not in network_dict.keys():
                                                    vport_list.append(
                                                        [enterprise.name, domain.name, zone.name, subnet.name,
                                                         domain.service_id, subnet.gateway, subnet.address,
                                                         subnet.netmask,
                                                         network_dict[subnet.id][0], network_dict[subnet.id][1],
                                                         network_dict[subnet.id][2], network_dict[subnet.id][3],
                                                         network_dict[subnet.id][4], network_dict[subnet.id][5],
                                                         network_dict[subnet.id][6], network_dict[subnet.id][7],
                                                         network_dict[subnet.id][8],
                                                         vport.name, vport.id, vport.associated_gateway_id, vport.vlan,
                                                         vport.vlanid,
                                                         '', '', '', '', '', '', ''])

                            page_num_1 += 1

                page_num += 1

        header = ['Enterprise', 'Domain', 'Zone', 'Subnet', 'Service_ID',
                  'Subnet_GW_IP', 'Subnet', 'Netmask',
                  'Bgp_nei_name', 'Bgp_peer_as', 'bgp_nei.peer_ip',
                  'import_routing_policy_id', 'export_routing_policy_id',
                  'bgp_nei_import_name', 'bp_nei_import_desp', 'bgp_nei_export_name', 'bgp_nei_export_desp']


        mpls_vvas_df = pd.DataFrame(bgp_list, columns=header)
        print(mpls_vvas_df)
        header = ['Enterprise', 'Domain', 'Zone', 'Subnet',
                  'Service_ID', 'Subnet_GW_IP', 'Subnet', 'Netmask',
                  ' Bgp_nei_name', 'Bgp_peer_as', 'bgp_nei.peer_ip',
                  'import_routing_policy_id', 'export_routing_policy_id',
                  'bgp_nei_import_name', 'gp_nei_import_desp', 'bgp_nei_export_name', 'bgp_nei_export_desp',
                  'Vport', 'vport.id', 'associated_GW_ID', 'VLAN', 'VLAN_ID', 'port.name', 'port.physical_name',
                  'GW_name',
                  'RG_peer1_name', 'RG_peer1_ID', 'RG_peer2_name', 'RG_peer2_ID']

        mpls_vvas_rg_df = pd.DataFrame(vport_list, columns=header)
        print (mpls_vvas_rg_df)

        ######  Commented for test only START ######
        header = ['Enterprise', 'Domain', 'Zone', 'Subnet', 'Service_ID',
                  'Subnet_GW_IP', 'Subnet', 'Netmask',
                  'Bgp_nei_name', 'Bgp_peer_as', 'bgp_nei.peer_ip',
                  'import_routing_policy_id', 'export_routing_policy_id',
                  'bgp_nei_import_name', 'bp_nei_import_desp', 'bgp_nei_export_name', 'bgp_nei_export_desp']
        filename = 'mpls_vvas.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in bgp_list:
                spamwriter.writerow(i)
        ######  Commented for test only END ######

        header = ['Enterprise', 'Domain', 'Zone', 'Subnet',
                  'Service_ID', 'Subnet_GW_IP', 'Subnet', 'Netmask',
                  ' Bgp_nei_name', 'Bgp_peer_as', 'bgp_nei.peer_ip',
                  'import_routing_policy_id', 'export_routing_policy_id',
                  'bgp_nei_import_name', 'gp_nei_import_desp', 'bgp_nei_export_name', 'bgp_nei_export_desp',
                  'Vport', 'vport.id', 'associated_GW_ID', 'VLAN', 'VLAN_ID', 'port.name', 'port.physical_name',
                  'GW_name',
                  'RG_peer1_name', 'RG_peer1_ID', 'RG_peer2_name', 'RG_peer2_ID']

        filename = 'mpls_vvas_rg.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in vport_list:
                spamwriter.writerow(i)
        ######  Commented for test only END ######

        return mpls_vvas_df, mpls_vvas_rg_df

    except Exception as e:
        print(e)
        return pd.DataFrame()

getNsgList()