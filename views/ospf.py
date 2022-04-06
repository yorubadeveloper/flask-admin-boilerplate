# Author:  Linda Tian  2022 April
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# Check NSG OSPF instance in domain level in API6
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

        ospf_list = []
        ospf_list_2 = []

        page_num = 0
        pagesize = 100

        # Get routing policy
        bgp_policy_dict = {}
        bgp_policy_dict_keys = ''
        bgp_policy_dict_values = []

        for enterprise in user.enterprises.get():
            # if enterprise.name == 'NaaS_Ref':
            for routing_policy in enterprise.routing_policies.get():
                # print (routing_policy.name, routing_policy.description, routing_policy.id )
                bgp_policy_dict_keys = routing_policy.id
                bgp_policy_dict_values = [routing_policy.name, routing_policy.description]
                bgp_policy_dict[bgp_policy_dict_keys] = bgp_policy_dict_values

            ############ Get routing policy bgp name dictionary ###########

        for enterprise in user.enterprises.get():
            # if enterprise.name == 'NaaS_Ref':
            pages = math.ceil(float(enterprise.domains.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }

                for domain in enterprise.domains.get(**page_filter):
                    if len(domain.ospf_instances.get()) != 0:
                        for ospf in domain.ospf_instances.get():
                            print(enterprise.name, domain.name, ospf.name, len(ospf.ospf_areas.get()), '---')
                            associated_import_routing_policy = ''
                            associated_export_routing_policy = ''
                            if ospf.associated_import_routing_policy_id in bgp_policy_dict.keys():
                                associated_import_routing_policy = \
                                bgp_policy_dict[ospf.associated_import_routing_policy_id][0]
                            if ospf.associated_export_routing_policy_id in bgp_policy_dict.keys():
                                associated_export_routing_policy = \
                                bgp_policy_dict[ospf.associated_export_routing_policy_id][0]
                            ospf_list.append(
                                [enterprise.name, domain.name, ospf.name, ospf.description, ospf.preference,
                                 ospf.associated_export_routing_policy_id, associated_export_routing_policy,
                                 ospf.associated_import_routing_policy_id, associated_import_routing_policy,
                                 ospf.super_backbone_enabled, ospf.export_limit, ospf.export_to_overlay,
                                 ospf.external_preference])

                            if len(ospf.ospf_areas.get()) != 0:
                                for area in ospf.ospf_areas.get():
                                    area_id = area.area_id
                                    area_type = area.area_type
                                    redistribute_external_enabled = area.redistribute_external_enabled
                                    default_metric = area.default_metric
                                    default_originate_option = area.default_originate_option
                                    aggregate_area_range = area.aggregate_area_range
                                    aggregate_area_range_nssa = area.aggregate_area_range_nssa
                                    summaries_enabled = area.summaries_enabled
                                    suppress_area_range = area.suppress_area_range
                                    suppress_area_range_nssa = area.suppress_area_range_nssa

                                    if len(area.ospf_interfaces.get()) != 0:
                                        pages_1 = math.ceil(float(area.ospf_interfaces.get_count()) / float(pagesize))
                                        page_num_1 = 0
                                        while page_num_1 < pages_1:
                                            page_filter = {
                                                'page_size': pagesize,
                                                'page': page_num_1
                                            }

                                            for interface in area.ospf_interfaces.get(**page_filter):
                                                interface_name = interface.name
                                                interface_description = interface.description
                                                interface_interface_type = interface.interface_type
                                                interface_passive_enabled = interface.passive_enabled
                                                interface_admin_state = interface.admin_state
                                                interface_dead_interval = interface.dead_interval
                                                interface_hello_interval = interface.hello_interval
                                                interface_message_digest_keys = interface.message_digest_keys
                                                interface_metric = interface.metric
                                                interface_creation_date = interface.creation_date
                                                interface_priority = interface.priority
                                                interface_associated_subnet_id = interface.associated_subnet_id
                                                interface_mtu = interface.mtu
                                                interface_authentication_key = interface.authentication_key
                                                interface_authentication_type = interface.authentication_type

                                                ospf_list_2.append(
                                                    [enterprise.name, domain.name, ospf.name, ospf.description,
                                                     ospf.preference,
                                                     ospf.associated_export_routing_policy_id,
                                                     associated_export_routing_policy,
                                                     ospf.associated_import_routing_policy_id,
                                                     associated_import_routing_policy,
                                                     ospf.super_backbone_enabled, ospf.export_limit,
                                                     ospf.export_to_overlay, ospf.external_preference,
                                                     area_id, area_type, redistribute_external_enabled, default_metric,
                                                     default_originate_option, aggregate_area_range,
                                                     aggregate_area_range_nssa,
                                                     summaries_enabled, suppress_area_range, suppress_area_range_nssa,
                                                     interface_name, interface_description, interface_interface_type,
                                                     interface_passive_enabled, interface_admin_state,
                                                     interface_dead_interval, interface_hello_interval,
                                                     interface_message_digest_keys, interface_metric,
                                                     interface_priority, interface_associated_subnet_id, interface_mtu,
                                                     interface_authentication_key, interface_authentication_type])

                                            page_num_1 += 1

                    page_num += 1
        header = ['Enterprise', 'Domain', 'ospf.name', 'ospf.description', 'ospf.ip_type', 'ospf.ospf_type',
                  'ospf.preference',
                  'ospf.associated_export_routing_policy_id', 'ospf.associated_export_routing_policy',
                  'ospf.associated_import_routing_policy_id', 'ospf.associated_import_routing_policy',
                  'ospf.super_backbone_enabled',
                  'ospf.export_limit', 'ospf.export_to_overlay', 'ospf.external_preference',
                  'area_id', 'area_type', 'redistribute_external_enabled', 'default_metric', 'default_originate_option',
                  'aggregate_area_range', 'aggregate_area_range_nssa',
                  'summaries_enabled',
                  'interface_name', 'interface_description', 'interface_interface_type',
                  'interface_passive_enabled', 'interface_admin_state', 'interface_dead_interval',
                  'interface_hello_interval',
                  'interface_message_digest_keys', 'interface_metric',
                  'interface_priority', 'interface_associated_subnet_id', 'interface_mtu',
                  'interface_authentication_key',
                  'interface_authentication_type']
        ospfdf = pd.DataFrame(ospf_list_2, columns=header)
        print (ospfdf)

        #### This can be commented for test only ####
        filename = 'OSPF.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in ospf_list_2:
                spamwriter.writerow(i)
        #### This can be commented for test only ####

        return ospfdf
    except Exception as e:
        print(e)
        return pd.DataFrame()

getRgVlanList()