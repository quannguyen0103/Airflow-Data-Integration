# Source

## Setup
- Install `Airflow`, `MySQL`, and `MongoDB`
- Create a `MySQL` database and a table within the database to store Newegg data: [setup_table](src/data_processing/Newegg/setup_database.py)
- Create a `MongoDB` database and a collection within the database to store Tiki data
- Create a `GCS bucket`
- Create two BigQuery datasets: a `staging area` for data preparation and processing, and a `final dataset` ready for analysis or deployment
- Set up a [Google Cloud connection](src/connection_configurating/cloud_connection.py) for `Airflow`
- Configure `Airflow SMTP` to send alert emails when a task failed

## Airflow
- Flow: Scrape & load data => Extract data => Migrate data => Load data to the data staging area => Transform and load data => Create data mart
- DAG: [process-data](src/dag)
  - Run at 7 AM every day
  - Retry 3 times, each time 5 minutes apart
  - Send an alert email when a task failed
  
### 1. Scrape & load data
- Scrape product data from the Tiki website and load it into the `tiki-data` collection in MongoDB: [load-tiki-data](src/data_processing/Tiki/scrape_data.py)
- Scrape product data from the Newegg website and load it into the `newegg-data` table in MySQL: [load-newegg-data](src/data_processing/Newegg/scrape_data.py)
  
### 2. Extract data
- Extract `newegg-data` table from `scraped_data` database in `MySQL` to `newegg_data.csv` file: [extract-newegg-data](src/data_processing/Newegg/extract_data.py)
- Extract `tiki-data` collection from `scraped_data` database in `MongoDB` to a `tiki_data.json` file: [extract-tiki-data](src/data_processing/Tiki/extract_data.py)
  - Use `sed` command to remove `HTML` tags in the `JSON` file: `sed -E 's/<[^>]*>//g'`
 
### 3. Migrate data
- Migrate `newegg_data.csv` ([migrate-Newegg-data](src/data_processing/Newegg/migrate_data.sh)) and `tiki_data.json` ([migrate-Tiki-data](src/data_processing/Tiki/migrate_data.sh)) file to a `GCS bucket`

### 4. Load data to the data staging area
- Load `newegg_data.csv` and `tiki_data.json` file from the `GCS bucket` to the `data staging area` in `BigQuery`

### 5. Transform and load data
- Transform tiki-data

```
SELECT
	*
	, (price * all_time_quantity_sold) total_revenue -- find total revenue of each product
  	, DATE_SUB(CURRENT_DATE(), INTERVAL day_ago_created DAY) created_date -- create the created_date column
FROM `project_id.staging_warehouse.tiki_data`
WHERE stock_item.qty is not null; -- get only products still in stock
```
- Load data from the `data staging area` to a database in `BigQuery`

### 5. Create data mart
- Create a data mart for other teams to use
  - Tiki-data:

  ```
  WITH product_origin AS
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
  	, p.origin
  FROM `project_id.scraped_data.tiki_data` t
  LEFT JOIN product_origin p ON t.id = p.id;
  ```

  - Newegg-data:
  ```
  SELECT
	itemID
	, brand
	, total_price
	, rating
  FROM `project_id.scraped_data.newegg_data`;
  ```
