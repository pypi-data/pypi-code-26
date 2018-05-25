import os
from google.cloud import bigquery
from google.cloud import storage

from optel.datalake import sanity_checks
from optel.datalake.ingest import write_parquet


def write_to_bigquery(df, table_name, *, dataset,
                      bucket, temp_zone="pyspark/tmp"):
    """
    Write a pyspark dataframe to google BigQuery. It uses a temporary folder
    in a google cloud storage bucket to do the operation. It then deletes
    everything it just wrote.

    .. Note: Needs to be run from a google cloud compute engine with access
             to google cloud storage and google big query.

    Args:
        df (pyspark.sql.DataFrame): DataFrame to write to BigQuery.
        table_name (str): Name to use in BigQuery.
        bucket (str): Google Cloud Storage Bucket to use for the temp folder.
        dataset (str): Name of the dataset in BigQuery.
        temp_zone (str): Name of the temp folder we'll use as staging.
    """
    df = sanity_checks.convert_decimal_to_float(df)
    df = sanity_checks.convert_date_to_string(df)
    write_parquet(df, os.path.join("gs://", bucket, temp_zone, table_name))

    storage_client = storage.Client()
    storage_bucket = storage_client.bucket(bucket)

    bq_client = bigquery.Client()
    bq_dataset = bq_client.dataset(dataset)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = "PARQUET"
    job_config.write_disposition = "WRITE_TRUNCATE"

    load_job = bq_client. \
        load_table_from_uri(os.path.join("gs://", bucket, temp_zone,
                                         table_name, "part-*"),
                            bq_dataset.table(table_name.replace(".", "")),
                            job_config=job_config)
    load_job.result()

    temp_blobs = storage_bucket.\
        list_blobs(prefix=os.path.join(temp_zone, table_name))
    [blob.delete() for blob in temp_blobs]
