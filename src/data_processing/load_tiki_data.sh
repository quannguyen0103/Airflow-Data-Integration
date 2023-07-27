BUCKET="scraped_data_201"
FILE="/home/user/pipeline_data/tiki_data.json"

gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" -m cp "$FILE" gs://"$BUCKET"
rm "$FILE"
