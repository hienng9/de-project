from fetch_and_save_data import *
from upload_to_gcs import *
import os
from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateExternalTableOperator,
)

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "secondhand_boats")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
dataset_file = f"secondhand-boats-{current_date}.parquet"

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="once_ingestion_gcs_dag",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=["once-veneet-tori.fi"],
) as dag:
  fetch_and_save_to_local_task = PythonOperator(
    task_id = "fetch_and_save_to_local_task",
    python_callable = fetch_all_and_save,
    op_kwargs = {
      "path": path_to_local_home,
      "number_of_pages": 68
    }
  )
  local_to_gcs_task = PythonOperator(
    task_id = "local_to_gcs_task",
    python_callable = upload_to_gcs,
    op_kwargs = {
      "bucket": BUCKET,
      "object_name": f"secondhand-boats/{dataset_file}",
      "local_file": f"{path_to_local_home}/{dataset_file}"
    }
  )
  bigquery_external_table_task = BigQueryCreateExternalTableOperator(
    task_id = "bigquery_external_table_task",
    table_resource = {
      "tableReference":{
        "projectId": PROJECT_ID,
        "datasetId": BIGQUERY_DATASET,
        "tableId": "external_table",
      },
      "externalDataConfiguration":{
        "sourceFormat":"PARQUET",
        "sourceUris": [f"gs://{BUCKET}/secondhand-boats/{dataset_file}"]
      }
    }
  )
  fetch_and_save_to_local_task >> local_to_gcs_task >> bigquery_external_table_task