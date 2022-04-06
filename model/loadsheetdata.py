from helpers.gcloud.service_incidents.mod_gcloud import *



def load_gsheet(gsheet_name, gsheet_tab):
    return get_gsheet_data(gsheet_name, gsheet_tab)