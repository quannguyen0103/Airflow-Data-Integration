import sqlalchemy as db
import pandas as pd

engine = db.create_engine("mysql+mysqlconnector://root:password@localhost:3306/scraped_data")
connection = engine.connect()
query = "select * from newegg_data"
query_df = pd.read_sql_query(query, engine)
query_df.to_csv("/home/user/pipeline_data/newegg_data.csv", index = False)
connection.close()
