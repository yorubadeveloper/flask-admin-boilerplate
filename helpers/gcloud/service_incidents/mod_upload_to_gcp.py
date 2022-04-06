'''
 # @ Author: Shengtao Li
 # @ Create Time: 2020-09-21 19:31:33
 # @ Modified by: Shengtao Li
 # @ Modified time: 2020-09-21 19:31:40
 # @ Description: Module for creating or updating GCP BigQuery from local or GCS csv file
 # @ Credits:
 '''

from google.cloud import storage

# The function is used when the env has a env_VAR GOOGLE_APPLICATION_CREDENTIALS that points to the dir of credential json file
def gcp_storage_upload(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

# Use this function to specify a key json file stored locally
def gcp_storage_upload_with_key(bucket_name, source_file_name, destination_blob_name, gcp_account_json_key):
    """Uploads a file to the bucket with key file provided."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    # gcp_account_json_key = "path to your json key file"
    storage_client = storage.Client.from_service_account_json(json_credentials_path = gcp_account_json_key)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )