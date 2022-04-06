
import config
import datetime
from mod_gcloud import get_service_incident_data
from mod_upload_to_gcp import gcp_storage_upload
import os

print('Credendtials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
gsheet_name = config.gsheet_name
tab_name = config.tab_name
bucket_name = config.bucket_name

# updated version that pushes only changes to cloud 
def main(event,context) :
    # get data 
    df_dict = get_service_incident_data(gsheet_name,tab_name)

    # save locally as CSV and upload to GCP
    time_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for key,value in df_dict.items() : 
        if value.empty == False: 
            tmp_file_path = "tmp/%s_incidents_%s.csv" % (key,time_str)
            value.to_csv(tmp_file_path,index=False)
            try : 
                gcp_storage_upload(bucket_name, tmp_file_path, f"{key}_incidents_update.csv")
                print("Successfully uploaded %s entries as %s to GCP." % (len(value),f"{key}_incidents_update.csv"))
            except Exception as e :
                print(f"ERROR: Failed to upload {key}_incidents_update.csv to GCP.")
        else : 
            print(f"{key} incidents data is already up-to-date! No file pushed.")


if __name__== "__main__" :
    main("","")