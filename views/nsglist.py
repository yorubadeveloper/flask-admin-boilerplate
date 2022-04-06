# Author:  Linda Tian  2021
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# Adding : port role and mode,  timezone, nat-t
# Updated with import vspk v6
# Modified in Aug 2021

# MOdified by :  Abisola Akinrinade  2022
# Email: abisola.akinrinade@telus.com
# Python 3 environment to access production VSD
# Adding : port role and mode,  timezone, nat-t
# Modified in March 2022


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
        nsg_list = []

        page_num = 0
        pagesize = 100

        nsg_template = {}
        infrastructure_profile = {}
        for template in user.ns_gateway_templates.get():
            nsg_template[template.id] = [template.name, template.infrastructure_profile_id]
        for infrastructure in user.infrastructure_gateway_profiles.get():
            infrastructure_profile[infrastructure.id] = [infrastructure.name, infrastructure.ntp_server_key]
        upgrade_profile = {}
        for profile in user.nsg_upgrade_profiles.get():
            upgrade_profile[profile.id] = profile.name

        for enterprise in user.enterprises.get():
            # if enterprise.name == 'CoT-Test-2':
            name_filter = "name is '{}'".format(enterprise.name)
            enterprise = user.enterprises.get_first(filter=name_filter)
            pages = math.ceil(float(enterprise.ns_gateways.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }

                for nsg in enterprise.ns_gateways.get(**page_filter):
                    # VSD gui shows the timetag  as us with vrs.uptime, make change to be readable
                    last_updated_date = time.ctime(nsg.last_updated_date / 1000)
                    creation_date = time.ctime(nsg.creation_date / 1000)
                    Speed_Offer =[]
                    Speed = []
                    for metadata in nsg.metadatas.get():
                        Speed_Offer.append(metadata.description)
                        Speed.append(metadata.blob)

                    if nsg.associated_nsg_upgrade_profile_id is not None:
                        Upgrade_Profile_Name = upgrade_profile[nsg.associated_nsg_upgrade_profile_id]
                    else:
                        Upgrade_Profile_Name = None
                    print(enterprise.name, nsg.system_id, nsg.name, nsg.bootstrap_status)
                    #########  Adding extra info of nsg link START ###########
                    port_mode = ''
                    port_role = ''
                    WAN1_NAT = ''
                    for uplink in nsg.uplink_connections.get():
                        if uplink.port_name == 'port1' or uplink.port_name == 'port3':
                            port_mode = uplink.mode
                            port_role = uplink.role
                    for port in nsg.ns_ports.get():
                        if "LAN" not in port.name:
                            if port.physical_name == 'port1' or port.physical_name == 'port3':
                                WAN1_NAT = port.enable_nat_probes

                    for location in nsg.locations.get():
                        timezone = location.time_zone_id
                    #########  Adding extra info of nsg link END ###########

                    nsg_list.append(
                        [nsg.name, nsg.system_id, enterprise.name, nsg.bootstrap_status, nsg.operation_status,
                         Speed_Offer, Speed, last_updated_date, creation_date, nsg.operation_mode,
                         nsg.gateway_connected, nsg.configuration_status, nsg.nsg_version, nsg.family,
                         nsg.tcpmss_enabled, nsg.tcp_maximum_segment_size, nsg.network_acceleration, nsg.tpm_status,
                         nsg.tpm_version,
                         nsg.product_name, nsg.serial_number,
                         nsg.aar_application_version, nsg.id, nsg.template_id, nsg_template[nsg.template_id][0],
                         nsg_template[nsg.template_id][1],
                         infrastructure_profile[nsg_template[nsg.template_id][1]][0],
                         infrastructure_profile[nsg_template[nsg.template_id][1]][1],
                         nsg.configuration_reload_state, nsg.configuration_status,
                         nsg.associated_nsg_upgrade_profile_id, Upgrade_Profile_Name,
                         port_mode, port_role, WAN1_NAT,
                         time.strftime("%Y-%m-%d", ts)])

                page_num += 1

        time_str = time.strftime("%Y%m%d-%H%M%S")
        header = ['NSG Name',
                  'Datapath ID',
                  'Enterprise',
                  'Status',
                  'Operation Status',
                  'Speed Offer',
                  'Speed',
                  'Last Updated Date',
                  'Creation Date',
                  'Operation Mode',
                  'Gateway Connected',
                  'Configuration Status',
                  'Version',
                  'NSG_Type',
                  'TCP MSS Enabled',
                  'TCP MSS',
                  'DPDK',
                  'TPM Status',
                  'TPM Version',
                  'product_name',
                  'serial_number',
                  'AAR Application Version',
                  'UUID',
                  'Template ID',
                  'Template Name',
                  'Infrastructure Profile ID',
                  'Infrastructure Profile Name',
                  'NTP_KEY',
                  'Sync State',
                  'Sync Status',
                  'Upgrade Profile ID',
                  'Upgrade Profile Name',
                  'WAN1_mode',
                  'WAN1_port',
                  'WAN1_NAT',
                  'Timestamp']

        nsgdf = pd.DataFrame(nsg_list, columns=header)
        print (nsgdf)

        ######  Commented for test only START ######
        filename = 'nsglist.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in nsg_list:
                spamwriter.writerow(i)
        ######  Commented for test only END ######

        return nsgdf
    except Exception as e:
        print(e)
        return pd.DataFrame()

getNsgList()