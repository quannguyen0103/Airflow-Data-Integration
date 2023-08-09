import datetime
from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
from airflow.utils import trigger_rule
from airflow.utils.dates import days_ago
from airflow.operators import dummy_operator
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

default_dag_args = {
	"start_date": days_ago(1)
	, "retries": 3
	, "retry_delay": datetime.timedelta(minutes=5)
	, "email": "quangcloud123@gmail.com"
	, "email_on_failure": True
	, "email_on_retry": True
}

tiki_sql_query = """SELECT
			*
			, (price * all_time_quantity_sold) total_revenue
			, DATE_SUB(CURRENT_DATE(), INTERVAL day_ago_created DAY) created_date
		FROM `project_id.staging_warehouse.tiki_data`
		WHERE stock_item.qty is not null;"""

dashboard_query = """WITH product_origin AS
			(
			SELECT
				h.id
				, h.categories.name category
				, a.value origin
			FROM `project_id.scraped_data.tiki_data` h
			, UNNEST(specifications) s
			, UNNEST(s.attributes) a
			WHERE a.name = 'Xuất xứ'
  			)
			SELECT
				t.id
				, t.categories.name category
				, t.current_seller.name seller_name
				, t.all_time_quantity_sold
				, t.price
				, t.rating_average
				, P.origin
			FROM `project_id.scraped_data.tiki_data` t
			LEFT JOIN product_origin p ON t.id = p.id;"""

with models.DAG("process_Tiki_data"
	, schedule_interval = "0 7 * * *"
	, default_args = default_dag_args) as dag:

	extract_data = bash_operator.BashOperator(
                task_id = "extract_data"
                , bash_command = "/home/user/src/data_processing/Tiki/extract_data.sh "
		, dag=dag
		,
)

	load_data_to_gcs = bash_operator.BashOperator(
		task_id = "load_data_to_gcs"
		, bash_command = "/home/user/src/data_processing/Tiki/migrate_data.sh "
		, dag=dag
		,
)

	load_data_to_staging_warehouse = GCSToBigQueryOperator(
                task_id = "load_data_to_staging_warehouse"
                , bucket = "scraped_data_201"
                , source_objects =["tiki_data.json"]
                , destination_project_dataset_table = "project_id.staging_warehouse.tiki_data"
                , source_format = "NEWLINE_DELIMITED_JSON"
                , write_disposition = "WRITE_TRUNCATE"
                , max_bad_records = 100
                , autodetect = True
                , gcp_conn_id = "gcp_connection"
                , encoding = "UTF-8"
                , create_disposition="CREATE_IF_NEEDED"
		, dag=dag
		,
)

	transform_and_load_data = BigQueryExecuteQueryOperator(
		task_id = "transform_and_load_data"
		, destination_dataset_table = "project_id.scraped_data.tiki_data"
		, gcp_conn_id = "gcp_connection"
		, create_disposition = "CREATE_IF_NEEDED"
		, sql = tiki_sql_query
		, use_legacy_sql = False
		, write_disposition = "WRITE_TRUNCATE"
		, dag=dag
		,
)

	create_data_mart = BigQueryExecuteQueryOperator(
		task_id = "create_table_for_dashboard"
		, destination_dataset_table = "project_id.dashboard.tiki_data"
		, gcp_conn_id = "gcp_connection"
		, create_disposition = "CREATE_IF_NEEDED"
		, sql = dashboard_query
		, use_legacy_sql = False
		, write_disposition = "WRITE_TRUNCATE"
		, dag=dag
		,
)

extract_data >> load_data_to_gcs >> load_data_to_staging_warehouse >> transform_and_load_data >> create_data_mart
