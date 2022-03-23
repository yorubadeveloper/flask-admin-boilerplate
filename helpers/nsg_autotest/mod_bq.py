from google.cloud import bigquery

def nsg_sysip_by_name(edge_name):
    # Construct a BigQuery client object.
    client = bigquery.Client()

    query = """
        SELECT systemIP
        FROM `dashboard-293900.nuage.nuage_edges`
        WHERE edgeName = @edge_name 
        
    """
    #AND (TIMESTAMP_DIFF(timeNow, timeStamp, MINUTE))<60
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("edge_name", "STRING", edge_name)
            #bigquery.ScalarQueryParameter("min_word_count", "INT64", 250),
        ]
    )
    query_job = client.query(query, job_config=job_config)  # Make an API request.

    for row in query_job:
        if row.systemIP:
            print("nsg IP is: \t{}".format(row.systemIP))
            return row.systemIP
    
    return None

def nsg_wanip_by_name(edge_name):
    # Construct a BigQuery client object.
    client = bigquery.Client()

    query = """
        SELECT uplinkIp
        FROM `dashboard-293900.nuage.aiops_nsg_list`
        WHERE edgeName = @edge_name 
        
    """
    #AND (TIMESTAMP_DIFF(timeNow, timeStamp, MINUTE))<60
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("edge_name", "STRING", edge_name)
            #bigquery.ScalarQueryParameter("min_word_count", "INT64", 250),
        ]
    )
    query_job = client.query(query, job_config=job_config)  # Make an API request.

    for row in query_job:
        if row.uplinkIp:
            print("nsg uplinkIP is: \t{}".format(row.uplinkIp))
            return row.uplinkIp
    
    return None 
    
if __name__ == "__main__":
    #main("", "")
    #nsg_sysip_by_name("sli_nsgp8_home")
    nsg_wanip_by_name("sli_nsgp8_home")
