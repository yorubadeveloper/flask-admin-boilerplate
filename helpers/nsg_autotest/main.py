'''
 # @ Author: Shengtao Li
 # @ Create Time: 2021-01-15 13:55:22
 # @ Modified by: Your name
 # @ Modified time: 2021-01-16 14:57:51
 # @ Description: GCF nsg_autotest will run diagnosic commands when triggered by pub/sub topic nsg-alert
 '''


import datetime
import json
import base64
import io
import requests
import sys
import json
import click
import os
import tabulate
import datetime
from pathlib import Path
from getpass import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import yaml
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
			datefmt="[%X]",  
			level=logging.DEBUG)

log = logging.getLogger()

from dotenv import load_dotenv
from jumpssh import SSHSession

from mod_upload_to_gcp import gcp_storage_upload
from mod_publish import pub_ticket
from mod_webhook import send_gchat, send_slack
# from mod_bq import nsg_sysip_by_name, nsg_wanip_by_name
from mod_nsg_sshcli import nsg_jmp_cmds
import  mod_nsg_checks
from mod_engine import es_engine

from mod_gsheet import edge_attr_by_name, get_kb_cc, get_config_by_label

# Bucket rules is enabled to delete object 2+ days since object was updated
bucket_name = "aiops_log_48hr"


# config = yaml.safe_load(open("config.yml", "r").read())
log.debug("get config from g-sheet \"aiops_config\"")
gsheet_name = "aiops_config"
label1 = "dev"
label2 = ""
cfg_dict = get_config_by_label(gsheet_name, label1, label2)

## g-chat room aiops_zabbix
# webhook_url_zbx = config.get("webhook_url_zbx")
webhook_url_zbx = cfg_dict["webhook_url_zbx"]
## g-chat room aiops_chatbot
# webhook_url_bot = config.get("webhook_url_bot")
webhook_url_bot = cfg_dict["webhook_url_bot"]
## slack TELUS-NaaS2 aiops_slack1
# webhook_url_slack1 = config.get("webhook_url_slack1")
webhook_url_slack1 = cfg_dict["webhook_url_slack1"]

## edge (nsg) info
# gsheet_name = config.get("gsheet_name")
gsheet_name = cfg_dict["zbx_nsg_gsheet"]
# nms_name = config.get("nms_name")
nms_name = cfg_dict["nms_name"]

DEBUG = True

# "vip-alert", "Triaged Zabbix Alert", attr_dict
# attr_dict={'Problem name': 'High ICMP ping loss', 'Host': 'Vip_MEF242', 'Severity': 'Warning', 'Operational data': 'Loss: 100 %'}

def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))

    edge_id = ""
    problem = ""

    if 'data' in event:
        name = base64.b64decode(event['data']).decode('utf-8')
    else:
        name = 'World'
    print('Hello {}!'.format(name))

    if 'attributes' in event:
        if DEBUG:        
            print(event['attributes'])
            print(event['attributes']['edge_id'])
            
        edge_id = event['attributes']['edge_id']

        problem = event['attributes']['problem']
        
        #state = json.loads(json.dumps(data['attributes']))
        #attr_dict = str2dict(event['attributes'])
        #if DEBUG:        
            #print(attr_dict)
        
        #pub_alert("vip-alert", "Triaged Zabbix Alert", attr_dict)

    else:
        raise ValueError('No data provided')

    #wanIP = nsg_wanip_by_name(edge_id)
    edge_attr = edge_attr_by_name(gsheet_name, nms_name, edge_id)

    wan_ip = edge_attr['uplinkIp']
    customer_name = edge_attr['customerName'] # to be used by SNOW

    if DEBUG:        
        #print(f'systemIP: {systemIP}')
        print(f'wan_ip: {wan_ip}')

    ###
    ### Two-Steps Expert System
    ### Step 1: 
    ###     1.1 read g-sheet kb_nsg
    ###     1.2 build list of (cmd, check) for collecting facts with label "s001"
    ###     1.3 excute cmds, collect outputs via a txt file and push to GCS
    ###     1.4 parse output file against each cmds via corresponding check function, and returm result
    ###     1.5 pass result to rule-engine to determine next step and msg
    ###

    ## step 1.1

    # cmds = ["nuage-bgp-show summary-all", "ovs-appctl vrf/list alubr0",  "ping google.com -c 5" ]
    kb_gsheet = "kb_nsg"
    # s101 : step 1 with rule enabled
    # s100 : step 1 with rule disabled
    label_check = "s101"
    label_uncheck = "s100"
    kb_select = get_kb_cc(kb_gsheet, label_check, label_uncheck)
    
    ## step 1.2
    # cmds = ["nuage-bgp-show summary-all", "ovs-appctl vrf/list alubr0",  "ping google.com -c 5" ]
    subjects = []
    cmds = []
    checks = []
    proc_tests = []
    
    for item in kb_select:
        subjects.append(item["subject"])
        cmds.append(item["api_cmd"])
        checks.append(item["f_check"])
        proc_tests.append(item["proc_tests"])

    ## step 1.3
    output_fn = nsg_jmp_cmds(edge_id, wan_ip, cmds)

    if "Failed" in output_fn:
        send_gchat(webhook_url_zbx, f'Failed to check {edge_id}. Detail: {output_fn}')
        send_gchat(webhook_url_bot, f'Failed to check {edge_id}. Detail: {output_fn}')
        return        

    # By default this flag enables uploading cmd_output file to GCS  
    upload_flag = True

    if upload_flag:
        dst_fn = edge_id + "_" + output_fn
        gcp_storage_upload(bucket_name, "/tmp/"+output_fn, dst_fn)
        gcs_url = "https://storage.cloud.google.com/aiops_log_48hr/" + dst_fn
        send_gchat(webhook_url_zbx, f'Analyzing results from {edge_id}. Detail: {gcs_url}')
        send_gchat(webhook_url_bot, f'Analyzing results from {edge_id}. Detail: {gcs_url}')    

    ## step 1.4
    # result= chk.check_ping("cmd_ping", output_fn)

    log.debug("identify rule enabled kb entries labelled by \"s101\"")
    label_check = "s101"
    label_uncheck = None
    kb_select = get_kb_cc(kb_gsheet, label_check, label_uncheck)

    subj_results = []

    for item in kb_select:
        subject = item["subject"]
        cmd = item["api_cmd"]
        f_to_call = getattr(mod_nsg_checks, item["f_check"])
        result, detail, *_ = f_to_call(cmd, output_fn)
        # the above result is specific to f_check, and should be either pass, ciritical or fail based on the ciriteria
        # however, this result is recorded as an entry of the subj_results, which will be processed by rule
        subj_results.append({subject:(result, detail)})



    ###
    ### Two-Steps Expert System
    ### Step 2: 
    ###     2.0 mod_engine and mod_rules are imported
    ###     2.1 Define or load the procedure, an ordered list
    ###     2.2 iterate rules through each subj_results, yeild list of next step as {subject: (action_msg)}                   
    ###     2.3 excute next step action
    ###
    
    ## step 2.1
    log.debug("identify proc_tests, for now start with  \"triage\"")
    proc_tests = ["triage"]

    ## step 2.2
    log.debug("pass the subj_results with rule enabled through es_engine")

    es_engine(edge_id, kb_select, proc_tests, subj_results, customer_name)

    ## step 2.3
    # log.debug("take next step/action based on result from es_engine")
    # if result:
    #     print('{} from edge {} looks good!'.format(subject, edge_id))
    #     pub_ticket("ticketing", f'Issue Dismissed - {subject} from edge looks good!', event['attributes'])
    #     send_gchat(webhook_url_zbx, f'Issue Dismissed - {subject} from {edge_id} looks good! Detail: {detail}')
    #     if 'bot' in problem:
    #         send_gchat(webhook_url_bot, f'Check of {subject} from {edge_id} looks good! Detail: {detail}')
    # else:
    #     print('{} from edge {} shows something wrong!'.format(subject, edge_id))
    #     pub_ticket("ticketing", f'Issue Confirmed - {subject} from {edge_id} failed!', event['attributes'])
    #     send_gchat(webhook_url_zbx, f'Issue Confirmed - {subject} from {edge_id} failed! Detail: {detail}')
    #     if 'bot' in problem:
    #         send_gchat(webhook_url_bot, f'{subject} from {edge_id} failed! Detail: {detail}')
    #     if not ('sli' or 'tom' in edge_id.lower()):
    #         send_slack(webhook_url_slack1, f'Issue Confirmed - {subject} from {edge_id} failed! Detail: {detail}')

    

    ##     2.2 iterate rules through each subj_results, yeild list of next step as {subject: (action_msg)}                   
    # subj_results[1]
    #   {'bgp': (False, 'BGP Alert!!! \n##### ... 0 = 0x0\n\n')}

    
if __name__ == "__main__":
    edge_id = "nsg_sli_nsgp8_home"
    event = {'attributes': {'edge_id': edge_id, 'problem': 'debug'}}
    
    class context(object):
        def __init__(self):
            self.event_id = ""
            self.timestamp = ""
    
    mycontext = context()

    main(event, mycontext)

    
    # sysip = "209.29.178.54"
    # cmds = ["nuage-bgp-show summary-all", "ovs-appctl vrf/list alubr0",  "ping google.com -c 5"]

    # output_fn = nsg_jmp_cmds(edge_id, sysip, cmds)
    
    # result= chk.check_ping(edge_id, output_fn)
    
    # if result:
    #     print('Ping from NSG to cisco.com looks good!')
    #     pub_ticket("ticketing", 'Issue Dismissed - NSGinfo from edge looks good!', event)
    #     send_gchat(webhook_url, f'Issue Dismissed - Nping from {edge_id} looks good! Detail: {result}')
    # else:
    #     print('Check from edge failed!')
    #     pub_ticket("ticketing", 'Issue Confirmed - NSGinfo from edge failed!', event)
    #     send_gchat(webhook_url, f'Issue Confirmed - Nping from {edge_id} lost! Detail: {result}')
    #     if not ('sli' or 'tom' in edge_id.lower()):
    #         send_slack(webhook_url_slack1, f'Issue Confirmed - Check from {edge_id} failed! Detail: {result}')
    