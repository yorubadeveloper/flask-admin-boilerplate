'''
 # @ Author: Shengtao Li
 # @ Create Time: 2021-02-05 09:00:56
 # @ Modified by: Your name
 # @ Modified time: 2021-02-05 09:03:00
 # @ Description: Reading g-sheet to locate IP or sysid of an Edge 
 '''

#coding:utf-8
# linda.tian@telus.com
# Nov 2020
# Read google sheet nsg_list storing to a data structure


import gspread
import pandas as pd

# The function is used when the env has a env_VAR GOOGLE_APPLICATION_CREDENTIALS that points to the dir of credential json file
# Read the google sheet "nsm_list"
# https://docs.google.com/spreadsheets/d/10sQYRZ8nSJYyoOKzpVG2YHGffiZroKxElhL032Hnrwg/edit?ts=5fac4b73#gid=0

# Sample nsg_dict:
# 'vco401-yul1.velocloud.net': ['vco160-usca1.velocloud.net', 'shengtao.li@telus.com', 'T3lu5123', '3000', '0.75', '1000', '0.75']

# Sample capacity_list
# nmsName    nmsCapacity    nmsThreshold    gwCapacity    gwThreshold
# vmanage-941927.viptela.net    2000    0.75    1000    0.75

#GOOGLE_APPLICATION_CREDENTIALS='C:/Users/t952287/Desktop/test/gcp/dashboard-293900-1.json'
GOOGLE_APPLICATION_CREDENTIALS="config.py"

def get_zbxhosts_info(gsheet_name, nms_name):
    
    gc = gspread.service_account(filename=GOOGLE_APPLICATION_CREDENTIALS)
    
    wks = gc.open(gsheet_name).sheet1
    
    data = wks.get_all_values()
    headers = data.pop(0)

    zbxhost_all_df = pd.DataFrame(data, columns=headers)
    zbxhost_single_df = zbxhost_all_df[zbxhost_all_df["nmsName"] == nms_name]
    zbxhost_single_nms_dict = zbxhost_single_df.to_dict('records')
    return (zbxhost_single_nms_dict)


def edge_attr_by_name(gsheet_name, nms_name, hostname):

    dicts = get_zbxhosts_info(gsheet_name, nms_name)
    
    result_dict = next((item for item in dicts if item["zbxHostname"] == hostname), None)
    
    return result_dict

def get_kb_by_label(gsheet_name, label1, label2):
    
    gc = gspread.service_account(filename=GOOGLE_APPLICATION_CREDENTIALS)
    
    wks = gc.open(gsheet_name).sheet1
    
    data = wks.get_all_values()
    headers = data.pop(0)

    kb_all_df = pd.DataFrame(data, columns=headers)
    kb_single_df = kb_all_df[(kb_all_df["label"] == label1) | (kb_all_df["label"] == label2)]
    kb_single_label_dict = kb_single_df.to_dict('records')
    return (kb_single_label_dict)

# get duos of cmd and check
def get_kb_cc(gsheet_name, label1, label2):

    dicts = get_kb_by_label(gsheet_name, label1, label2)
    
    result_list = []
    while dicts:
        result_list.append({key: value for key, value in dicts.pop(0).items() if key in ["subject", "api_cmd", "f_check", "proc_tests"]})
    
    return result_list

def get_config_by_label(gsheet_name, label1, label2):
    gc = gspread.service_account(filename=GOOGLE_APPLICATION_CREDENTIALS)
    
    wks = gc.open(gsheet_name).sheet1
    
    data = wks.get_all_values()
    headers = data.pop(0)

    cfg_all_df = pd.DataFrame(data, columns=headers)
    cfg_select_df = cfg_all_df[(cfg_all_df["label"] == label1) | (cfg_all_df["label"] == label2)]
    dicts = cfg_select_df.to_dict('records')

    result_dict = {}
    while dicts:
        # result_list.append({key: value for key, value in dicts.pop(0).items() if key in ["key", "value"]})
        for key, value in dicts.pop(0).items():
            if key not in ["key", "value"]:
                continue
            
            if key == "key":
                new_key = value
    
            if key == "value":
                new_value = value
        
        result_dict[new_key] = new_value
    
    return result_dict



if __name__ == "__main__":
    #gsheet_name = "zbxhost_nsg_list"
    #hostname = "nsg_sli_nsgp8_home"
    #nms_name = "naas_vsd"
    #attr_list = ["edgeName", "uplinkIp"]
    # dict = get_zbxhost_info(gsheet_name, "naas_vsd")
    #result = edge_attr_by_name(gsheet_name, nms_name, hostname)
    #wanIP = result['uplinkIp']

    #print(wanIP)

    ###
    ### Test get_kb_cc
    ###
    # gsheet_name = "kb_nsg"
    # label1 = "s101"
    # label2 = "s100"
    # result = get_kb_cc(gsheet_name, label1, label2)
    # #cmds = result['uplinkIp']
    # print(result)


    ###
    ### Test get_config_by_label
    ###
    gsheet_name = "aiops_config"
    label1 = "dev"
    label2 = ""
    
    cfg_dict = get_config_by_label(gsheet_name, label1, label2)
    
    cfg_key = "webhook_url_zbx"
    result = cfg_dict[cfg_key]

    print(result)

