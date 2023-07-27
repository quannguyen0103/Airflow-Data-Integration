# Source

## Setup
- Install `Airflow` on the same environment as MySQL and MongoDB
- Create a `GCS bucket`
- Create two BigQuery datasets: a `staging area` for data preparation and processing, and a `final dataset` ready for analysis or deployment
- Set up a `Google Cloud connection` for `Airflow`
- Configure `Airflow SMTP` to send alert emails when a task failed

## ETL Flow
- ETL Flow: Extract data => Migrate data => Load data to the data staging area => Transform and load data => Create data mart
- DAG: [process-data](src/dag)
  - Run at 7 AM every day
  - Retry 3 times, each time 5 minutes apart
  - Send an alert email when a task failed

### 1. Extract data
- Extract data from 
