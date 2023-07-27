import datetime
from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
from airflow.utils import trigger_rule
from airflow.utils.dates import days_ago
from airflow.operators import dummy_operator
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.email import send_email

# Define dag_args
default_dag_args = {
	"start_date": datetime.datetime(2023, 7, 20)
	, "retries": 0
	, "retry_delay": datetime.timedelta(minutes=5)
	, "email": "samplemail123@gmail.com"
	, "email_on_failure": True
	, "email_on_retry": True
}

# Define queries
newegg_sql_query = """SELECT
			*
		FROM `project_id.staging_warehouse.newegg_data`;"""

dashboard_query = """SELECT
			itemID
			, brand
			, total_price
			, rating
		FROM `project_id.scraped_data.newegg_data`;"""

with models.DAG("process_Newegg_data"
	, schedule_interval = "0 7 * * *"
	, default_args = default_dag_args) as dag:

	extract_data = bash_operator.BashOperator(
		task_id = "extract_data"
		, bash_command = "python3 /home/user/pipeline_script/extract_newegg_data.py"
		, dag=dag
		,
)

	load_data_to_gcs = bash_operator.BashOperator(
		task_id = "load_data_to_gcs"
		, bash_command = "/home/user/pipeline_script/load_newegg_data.sh "
		, dag=dag
		,
)

	load_data_to_staging_warehouse = GCSToBigQueryOperator(
		task_id = "load_data_to_staging_warehouse"
		, bucket = "scraped_data_201"
		, source_objects =["newegg_data.csv"]
		, destination_project_dataset_table = "project_id.staging_warehouse.newegg_data"
		, source_format = "CSV"
		, write_disposition = "WRITE_TRUNCATE"
		, max_bad_records = 100
		, autodetect = True
		, gcp_conn_id = "gcp_connection"
		, encoding = "UTF-8"
		, create_disposition= "CREATE_IF_NEEDED"
		, dag=dag
		,
)

	transform_and_load_data = BigQueryExecuteQueryOperator(
                task_id = "transform_and_load_data"
                , destination_dataset_table = "project.scraped_data.newegg_data"
                , gcp_conn_id = "gcp_connection"
                , create_disposition = "CREATE_IF_NEEDED"
                , sql = newegg_sql_query
                , use_legacy_sql = False
		, write_disposition = "WRITE_TRUNCATE"
		, dag=dag
		,
)

	create_data_mart = BigQueryExecuteQueryOperator(
		task_id = "create_table_for_dashboard"
		, destination_dataset_table = "project_id.dashboard.newegg_data"
		, gcp_conn_id = "gcp_connection"
		, create_disposition = "CREATE_IF_NEEDED"
		, sql = dashboard_query
		, use_legacy_sql = False
		, write_disposition = "WRITE_TRUNCATE"
		, dag=dag
		,
)

extract_data >> load_data_to_gcs >> load_data_to_staging_warehouse >> transform_and_load_data >> create_data_mart
