# Author:  Linda Tian  2022 March
# Email: linda.tian@telus.com
# Python 3 environment to access production VSD
# 0utput is 4 pd frame: Domain_aar, domain_npm, apm, npm
# Updated with import vspk v6
# Refer structure to Abisola's nsglist module for db portal March 20, 2022
# # MOdified by :  Abisola Akinrinade  2022
# # Email: abisola.akinrinade@telus.com

from vspk import v6 as vspk
import time
import math
import pandas as pd
# import csv

def getAarNpmList(username='', password='', api_url='', enterprise='', certificate=None):

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

        applications_list = []
        apm_list = []
        npm_list = []
        apm_check = ''
        npm_check = ''

        DOMAIN_APM_list = []
        DOMAIN_NPM_list = []
        DOMAIN_LIST_APM_NPM_check = []

        network_dict = {}

        page_num = 0
        pagesize = 100

        print('Collecting Network_id and with name from Domain APM group, Application Bindings, Network Performance Measurement, monitorscope')
        # # Read from a specific enterprise
        # enterprise_name ='NaaS_Ref'
        # name_filter = "name is '{}'".format(enterprise_name)
        # enterprise = user.enterprises.get_first(filter=name_filter)
        for enterprise in user.enterprises.get():
            # if enterprise.name == 'NaaS_Ref':
            for applications in enterprise.applications.get():
                if applications.id not in network_dict.keys():
                    network_dict[applications.id] = [applications.name, applications.description, applications.app_id,
                                                     applications.associated_l7_application_signature_id,
                                                     applications.destination_ip, applications.destination_port,
                                                     applications.source_ip, applications.source_port,
                                                     applications.destination_ip, applications.destination_port,
                                                     applications.source_ip, applications.source_port,
                                                     applications.dscp, applications.enable_pps,
                                                     applications.ether_type, applications.network_symmetry,
                                                     applications.one_way_delay, applications.one_way_jitter,
                                                     applications.one_way_loss,
                                                     applications.optimize_path_selection,
                                                     applications.performance_monitor_type,
                                                     applications.pre_classification_path,
                                                     applications.pre_classification_path, applications.protocol]

                    applications_list.append(
                        [enterprise.name, applications.name, applications.description, applications.app_id,
                         applications.associated_l7_application_signature_id,
                         applications.dscp, applications.enable_pps, applications.ether_type,
                         applications.network_symmetry, applications.one_way_delay, applications.one_way_jitter,
                         applications.one_way_loss,
                         applications.optimize_path_selection, applications.performance_monitor_type,
                         applications.pre_classification_path,
                         applications.pre_classification_path, applications.protocol])

            for pm in enterprise.performance_monitors.get():
                if pm.id not in network_dict.keys():
                    network_dict[pm.id] = [pm.name, pm.description, pm.service_class, pm.payload_size, pm.interval,
                                           pm.hold_down_timer, pm.number_of_packets, pm.probe_type]
                    # print (pm.name,pm.description,  pm.service_class, pm.payload_size, pm.interval, pm.hold_down_timer, pm.number_of_packets, pm.probe_type)

            pages = math.ceil(float(enterprise.ns_gateways.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }
                for nsg in enterprise.ns_gateways.get(**page_filter):
                    network_dict[nsg.id] = [nsg.id, nsg.system_id, nsg.name]
                    # print (nsg.id, nsg.system_id, nsg.name)
                page_num += 1

            for npm in enterprise.network_performance_measurements.get():
                if npm.id not in network_dict.keys():
                    network_dict[npm.id] = [npm.name, npm.npm_type, npm.description,
                                            network_dict[npm.associated_performance_monitor_id]]
                    # print(enterprise.name, npm.name, npm.npm_type, npm.description,
                    #       network_dict[npm.associated_performance_monitor_id])

        # print (network_dict)
        print('Collecting APM and NPM levle data')
        # # Read from a specific enterprise
        # enterprise_name ='NaaS_Ref'
        # name_filter = "name is '{}'".format(enterprise_name)
        # enterprise = user.enterprises.get_first(filter=name_filter)
        for enterprise in user.enterprises.get():

            for apm in enterprise.applicationperformancemanagements.get():
                if apm.id not in network_dict.keys():
                    network_dict[apm.id] = [apm.name, apm.description, apm.app_group_unique_id,
                                            apm.associated_performance_monitor_id]
                    if len(apm.application_bindings.get()) != 0:
                        for application_binding in apm.application_bindings.get():
                            apm_list.append([enterprise.name, apm.name, apm.description,
                                             network_dict[application_binding.associated_application_id][0],
                                             application_binding.priority])

            for npm in enterprise.network_performance_measurements.get():
                # print(enterprise.name, npm.name, npm.description, '---')
                if len(npm.monitorscopes.get()) != 0:
                    for scope in npm.monitorscopes.get():
                        # print (len(scope.source_nsgs), len(scope.destination_nsgs))
                        soucre_nsg = ''
                        destination_nsg = ''
                        for i in scope.source_nsgs:
                            if i in network_dict.keys():
                                soucre_nsg = soucre_nsg + '_' + network_dict[i][2]
                        for j in scope.destination_nsgs:
                            if j in network_dict.keys():
                                destination_nsg = destination_nsg + '_' + network_dict[j][2]

                        npm_list.append([enterprise.name, npm.name, npm.description,
                                         network_dict[npm.associated_performance_monitor_id][0],
                                         network_dict[npm.associated_performance_monitor_id][1],
                                         network_dict[npm.associated_performance_monitor_id][2],
                                         network_dict[npm.associated_performance_monitor_id][3],
                                         network_dict[npm.associated_performance_monitor_id][4],
                                         network_dict[npm.associated_performance_monitor_id][5],
                                         network_dict[npm.associated_performance_monitor_id][6],
                                         network_dict[npm.associated_performance_monitor_id][7],
                                         scope.name, scope.allow_all_destination_nsgs, scope.allow_all_source_nsgs,
                                         soucre_nsg,
                                         destination_nsg])
                else:
                    npm_list.append([enterprise.name, npm.name, npm.description,
                                     network_dict[npm.associated_performance_monitor_id][0],
                                     network_dict[npm.associated_performance_monitor_id][1],
                                     network_dict[npm.associated_performance_monitor_id][2],
                                     network_dict[npm.associated_performance_monitor_id][3],
                                     network_dict[npm.associated_performance_monitor_id][4],
                                     network_dict[npm.associated_performance_monitor_id][5],
                                     network_dict[npm.associated_performance_monitor_id][6],
                                     network_dict[npm.associated_performance_monitor_id][7],
                                     '', '', '', '', ''])

        print('Collecting domain levle data')
        # Domain level data checking and collection

        # enterprise_name ='NaaS_Ref'
        # name_filter = "name is '{}'".format(enterprise_name)
        # enterprise = user.enterprises.get_first(filter=name_filter)
        for enterprise in user.enterprises.get():
            pages = math.ceil(float(enterprise.domains.get_count()) / float(pagesize))
            page_num = 0
            while page_num < pages:
                page_filter = {
                    'page_size': pagesize,
                    'page': page_num
                }
                for domain in enterprise.domains.get(**page_filter):
                    len_applicationperformancemanagementbinding = len(
                        domain.applicationperformancemanagementbindings.get())
                    len_network_performance_bindings = len(domain.network_performance_bindings.get())
                    if len_applicationperformancemanagementbinding != 0:
                        apm_check = 'AAR'
                        for apm_binding in domain.applicationperformancemanagementbindings.get():
                            # print(enterprise.name, domain.name, '----APM----',
                            #       len_applicationperformancemanagementbinding,
                            #       network_dict[apm_binding.associated_application_performance_management_id][0],
                            #       apm_binding.priority)
                            DOMAIN_APM_list.append([enterprise.name, domain.name, network_dict[
                                apm_binding.associated_application_performance_management_id][0], apm_binding.priority])
                    if len_network_performance_bindings != 0:
                        npm_check = 'NPM'
                        for npm_binding in domain.network_performance_bindings.get():
                            DOMAIN_NPM_list.append([enterprise.name, domain.name,
                                                    network_dict[npm_binding.associated_network_measurement_id][0],
                                                    npm_binding.priority])
                    DOMAIN_LIST_APM_NPM_check.append(
                        [enterprise.name, domain.name, apm_check, len_applicationperformancemanagementbinding,
                         npm_check, len_network_performance_bindings])

                page_num += 1

        header = ['Enterprise', 'Domain',  'AAR', 'Priority']
        Domain_aardf = pd.DataFrame(DOMAIN_APM_list, columns=header)
        header = ['Enterprise', 'Domain', 'NPM', 'Priority']
        Domain_npmdf = pd.DataFrame(DOMAIN_NPM_list, columns=header)
        header = ['Enterprise', 'applications.name', 'description', 'app_id', 'associated_l7_application_signature_id',
                  'applications.dscp', 'enable_pps', 'ether_type', 'network_symmetry',
                  'one_way_delay', 'one_way_jitter', 'one_way_loss',
                  'optimize_path_selection', 'performance_monitor_type', 'pre_classification_path',
                  'pre_classification_path', 'protocol']
        appdf = pd.DataFrame(applications_list, columns=header)
        header = ['Enterprise', 'AAR.name', 'description', 'Associated app Name', 'Priority']
        apmdf = pd.DataFrame(apm_list, columns=header)
        header = ['Enterprise', 'NPM.name', 'description',
                  'pm.name', 'pm.description', 'pm.service_class', 'pm.payload_size', 'pm.interval',
                  'pm.hold_down_timer', 'pm.number_of_packets', 'pm.probe_type',
                  'scope.name', 'scope.allow_all_destination_nsgs', 'scope.allow_all_source_nsgs', 'soucre_nsg',
                  'destination_nsg']
        npmdf = pd.DataFrame(npm_list, columns=header)

        print (Domain_aardf)
        print ('#'*100)
        print (Domain_npmdf)
        print('#' * 100)
        print (appdf)
        print('#' * 100)
        print (apmdf)
        print ('#'*100)
        print (npmdf)

        '''
        ### The following only for testing save to csv file, can be commented ###
        # header = ['Enterprise', 'Domain', 'AAR', '# APM bindings', 'NPM', '# NPM bindings']
        # filename = 'Domain_APM_NPM_check.csv'
        # with open(filename, 'w', newline='') as csvfile:
        #     spamwriter = csv.writer(csvfile, delimiter=',',
        #                             quotechar=',', quoting=csv.QUOTE_MINIMAL)
        #     spamwriter.writerow(header)
        #     for i in DOMAIN_LIST_APM_NPM_check:
        #         spamwriter.writerow(i)

        header = ['Enterprise', 'Domain', 'AAR', 'Priority']
        filename = 'Domain_AAR.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in DOMAIN_APM_list:
                spamwriter.writerow(i)

        header = ['Enterprise', 'Domain', 'NPM', 'Priority']
        filename = 'Domain_NPM.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in DOMAIN_NPM_list:
                spamwriter.writerow(i)
        header = ['Enterprise', 'Domain', 'AAR', 'Priority']
        filename = 'Domain_APM.csv'
        
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in DOMAIN_APM_list:
                spamwriter.writerow(i)

        header = ['Enterprise', 'Domain', 'NPM', 'Priority']
        filename = 'Domain_NPM.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in DOMAIN_NPM_list:
                spamwriter.writerow(i)

        header = ['Enterprise', 'applications.name', 'description', 'app_id', 'associated_l7_application_signature_id',
                  'applications.dscp', 'enable_pps', 'ether_type', 'network_symmetry',
                  'one_way_delay', 'one_way_jitter', 'one_way_loss',
                  'optimize_path_selection', 'performance_monitor_type', 'pre_classification_path',
                  'pre_classification_path', 'protocol']
        filename = 'Application.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in applications_list:
                spamwriter.writerow(i)

        header = ['Enterprise', 'AAR.name', 'description', 'Associated app Name', 'Priority']
        filename = 'APM.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in apm_list:
                spamwriter.writerow(i)

        header = ['Enterprise', 'NPM.name', 'description',
                  'pm.name', 'pm.description', 'pm.service_class', 'pm.payload_size', 'pm.interval',
                  'pm.hold_down_timer', 'pm.number_of_packets', 'pm.probe_type',
                  'scope.name', 'scope.allow_all_destination_nsgs', 'scope.allow_all_source_nsgs', 'soucre_nsg',
                  'destination_nsg']

        filename = 'NPM.csv'
        with open(filename, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(header)
            for i in npm_list:
                print(i)
                spamwriter.writerow(i)
        '''

        return Domain_aardf, Domain_npmdf, appdf, apmdf, npmdf
    except Exception as e:
        print(e)
        return pd.DataFrame()

getAarNpmList()