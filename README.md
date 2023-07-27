# Source

## Setup
- Install `Airflow` on the same environment as MySQL and MongoDB
- Create a `GCS bucket`
- Create two BigQuery datasets: a `staging area` for data preparation and processing, and a `final dataset` ready for analysis or deployment

## ETL Flow
- ETL Flow: Extract data >> Migrate data >> Load data to the data staging area >> Transform and load data >> Create data mart
- DAG: [process-data](src/dag)

### 1. Extract data
- Extract data from 
