DATABASE="scraped_data"
COLLECTION="tiki_data"
FILE="/home/user/pipeline_data/tiki_data.json"

mongoexport --db "$DATABASE" --collection "$COLLECTION" | sed '/"_id":/s/"_id":[^,]*,//'| sed -E 's/<[^>]*>//g' > "$FILE"
