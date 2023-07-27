# Source

## Setup
- Install `Airflow` on the same environment as MySQL and MongoDB
- Create a `GCS bucket`
- Create two BigQuery datasets: a `staging area` for data preparation and processing, and a `final dataset` ready for analysis or deployment
- Set up a [Google Cloud connection](src/connection_configurating/cloud_connection.py) for `Airflow`
- Configure `Airflow SMTP` to send alert emails when a task failed

## ETL Flow
- ETL Flow: Extract data => Migrate data => Load data to the data staging area => Transform and load data => Create data mart
- DAG: [process-data](src/dag)
  - Run at 7 AM every day
  - Retry 3 times, each time 5 minutes apart
  - Send an alert email when a task failed

### 1. Extract data
- Extract `newegg-data` table from `scraped_data` database in `MySQL` to a `CSV` file: [extract-newegg-data](src/data_processing/extract_newegg_data.py)
- Extract `tiki-data` collection from `scraped_data` database in `MongoDB` to a `JSON` file: [extract-tiki-data](src/data_processing/extract_tiki_data.py)
  - Use `sed` command to remove `HTML` tags in the `JSON` file: `sed -E 's/<[^>]*>//g'`
