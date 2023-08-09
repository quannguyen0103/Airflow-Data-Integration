#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import sqlalchemy as db

#Create a MySQL database
engine = db.create_engine("mysql+mysqlconnector://root:password@localhost:3306")
connection = engine.connect()
engine.execute("CREATE DATABASE scraped_data;")


# Define a table in scraped_data database
engine = db.create_engine("mysql+mysqlconnector://root:password@localhost:3306/scraped_data")
connection = engine.connect()

metadata = db.MetaData()

graphic_cards = db.Table("graphic_cards",
                         metadata,
                         db.Column("id", db.Integer(), primary_key = True, unique = True),
                         db.Column("itemID", db.String(255)),
                         db.Column("title", db.String(255)),
                         db.Column("brand", db.String(255)),
                         db.Column("rating", db.Float()),
                         db.Column("num_ratings", db.Integer()),
                         db.Column("price", db.Float()),
                         db.Column("shipping", db.Float()),
                         db.Column("img_url", db.String(255)),
                         db.Column("features", db.JSON()),
                         db.Column("total_price", db.Float()))
metadata.create_all(engine)