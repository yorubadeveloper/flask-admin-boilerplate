
import config
import gspread
import pandas as pd
import datetime
import google.auth
from google.cloud import bigquery
from google.cloud import bigquery_storage

GOOGLE_APPLICATION_CREDENTIALS = config.GOOGLE_APPLICATION_CREDENTIALS
# gsheet_name = config.gsheet_name
# tab_name = config.tab_name

def get_gsheet_data(gsheet_name,tab_name):

    # get data from google sheet 
    doc = gspread.service_account(filename=GOOGLE_APPLICATION_CREDENTIALS)
    gsheet = doc.open(gsheet_name).worksheet(tab_name)

    # save as pandas dataframe
    gsheet_dataframe = pd.DataFrame(gsheet.get_all_records())
    # print(gsheet_dataframe)

    # force datatypes
    df_datatypes = {"uuid":str,
        "vendorTicketNumber":str,
        "ticketNumber":str,
        "ticketStatus":str,
        "contactName":str,
        "sevLevel":'Int64',
        "isServiceImpacting":str,
        "pointOfFailure":str,
        "rootCause":str,
        "customerInfo":str,
        "ticketSummary":str,
        "numAffectedCustomers":'Int64',
        "numAffectedSites":'Int64',
        "totalSites":'Int64',
        "timeToRestore":float,
        "vendorName":str
    }
    int_types = ['sevLevel','numAffectedCustomers','numAffectedSites','totalSites','timeToRestore']
    gsheet_dataframe[int_types] = gsheet_dataframe[int_types].apply(pd.to_numeric,errors='coerce')
    gsheet_dataframe = gsheet_dataframe.astype(df_datatypes)

    return gsheet_dataframe


def format_data(naas_df) :
    # remove excess whitespace for proper CSV formatting
    n_total = []
    for col in naas_df :
        if naas_df[col].dtypes == "object" : 
            n_num = naas_df[col].str.contains('\n', regex=True).sum()
            n_total.append(n_num)

    for _ in range(max(n_total)) :       
        naas_df = naas_df.replace('\n',' ', regex=True) 

    # get all entries 
    updated_df = naas_df

    # isolate by vendor
    velo_query = "vendorName == 'VeloCloud'"
    velo_df = updated_df.query(velo_query)
    # print(velo_df)
    vip_query = "vendorName == 'Viptela'"
    vip_df = updated_df.query(vip_query)
    # print(vip_df)
    nuage_query = "vendorName == 'Nuage'"
    nuage_df = updated_df.query(nuage_query) 
    # print(nuage_df)

    return {'velo': velo_df, 'viptela': vip_df, 'nuage': nuage_df}


def get_service_incident_data(gsheet_name,tab_name) : 

    # get gsheet data 
    gsheet_df = get_gsheet_data(gsheet_name,tab_name)

    # set credentials 
    credentials, your_project_id = google.auth.load_credentials_from_file(GOOGLE_APPLICATION_CREDENTIALS,scopes=["https://www.googleapis.com/auth/cloud-platform"])

    # make clients
    bqclient = bigquery.Client(credentials=credentials, project=your_project_id,)
    bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)

    # get updated data 
    gs_dict = format_data(gsheet_df)

    df_dict = {}

    for key,gs_df in gs_dict.items() : 

        # determine dataset from vendor
        if key == "velo" : 
            dataset_name = "velocloud_ca"
        elif key == "viptela" : 
            dataset_name = "viptela_ca"
        elif key == "nuage" : 
            dataset_name = "nuage"
        else : 
            dataset_name = key

        # dynamically get table name based on vendor
        table_id = f"dashboard-293900.{dataset_name}.{key}_incidents"

        # get contents of BQ table
        query_string = f"""
            SELECT
            *
            FROM (
            SELECT
                *
            FROM
                `{table_id}`)
            ORDER BY
            timeStamp ASC"""

        # save as pandas dataframe
        bq_df = (
            bqclient.query(query_string)
            .result()
            .to_dataframe(bqstorage_client=bqstorageclient)
        )

        # force datatypes
        df_datatypes = {"uuid":str,
            "vendorTicketNumber":str,
            "ticketNumber":str,
            "ticketStatus":str,
            "contactName":str,
            "sevLevel":'Int64',
            "isServiceImpacting":str,
            "pointOfFailure":str,
            "rootCause":str,
            "customerInfo":str,
            "ticketSummary":str,
            "numAffectedCustomers":'Int64',
            "numAffectedSites":'Int64',
            "totalSites":'Int64',
            "timeToRestore":float,
            "vendorName":str
        }
        int_types = ['sevLevel','numAffectedCustomers','numAffectedSites','totalSites','timeToRestore']
        bq_df[int_types] = bq_df[int_types].apply(pd.to_numeric,errors='coerce')
        bq_df = bq_df.astype(df_datatypes)
        bq_df = bq_df.replace('None','', regex=True) 

        # iterate through dataframe and separate into entries to add and entries to remove
        bq_remove = [] # to delete from BQ for replacement or full removal 
        bq_add = [] # to add to BQ as replacement or new entries

        # isolate changed data
        for gs_idx,gs_row in gs_df.iterrows() : 
            # if uuid exists in BQ
            # print(f"{gs_row['uuid']}: {not bq_df[bq_df['uuid'].isin([gs_row['uuid']])].empty}")
            if not bq_df[bq_df['uuid'].isin([gs_row['uuid']])].empty : 
                for bq_idx,bq_row in bq_df.iterrows() : 
                    if gs_row['uuid'] == bq_row['uuid'] : 
                        gs_ts = datetime.datetime.strptime(str(gs_row['timeStamp']),'%Y-%m-%d %H:%M:%S')
                        bq_ts = datetime.datetime.strptime(str(bq_row['timeStamp'].replace(tzinfo=None)),'%Y-%m-%d %H:%M:%S')
                        if gs_ts != bq_ts : 
                            bq_remove.append(bq_row['uuid'])
                            bq_add.append(gs_idx)
            # if uuid does not exist in BQ
            else : 
                bq_add.append(gs_idx)

        update_df = gs_df[gs_df.index.isin(bq_add)]        

        # print(f"to add to bq: {update_df}")
        # print(f"to remove from bq: {bq_remove}")

        # remove corresponding entries from existing BQ table 
        for change in bq_remove :
            delete_query = f"""DELETE `{table_id}` WHERE uuid='{change}'"""
            delete = bqclient.query(delete_query)
            delete.result()

        # combine corresponding entries 
        df_dict[f'{key}'] = update_df

    # print(df_dict)    

    return df_dict
