#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import sqlalchemy as db

#1. Define functions to extract graphic cards information
# function used to extract card itemid
def extract_itemid(cb):
    return cb.get("id")

# function used to extract card titles
def extract_title(cb):
    str_title = cb.find("a", class_= "item-title")
    if str_title is not None:
        return cb.find("a", class_= "item-title").text
    else:
        return "NULL"

# function used to extract card rating
def extract_brand(cb):
    img_tag = cb.find('a', class_='item-brand')
    if img_tag is not None:
            img_tag = cb.find('a', class_='item-brand').find('img')
            if img_tag is not None:
                return img_tag['alt']
            else:
                return "NULL"
    else:
        return "NULL"

# function used to extract card rating
def extract_rating(cb):
    str_rating = cb.find("i")
    if str_rating is not None:
        rating = str_rating.get("aria-label")
        if rating is not None:
            return float(rating.split(" ")[1].strip())
        else:
            return 0.0
    else:
        return 0.0

# function used to extract card number of ratings
def extract_num_ratings(cb):
    str_num_ratings = cb.find("a", class_="item-rating")
    if str_num_ratings is not None:
        return int(str_num_ratings.text.strip("()"))
    else:
        return 0

# function used to extract card prices
def extract_price(cb):
    price_current = cb.find("li", class_ = "price-current")
    if price_current is not None:
        strong_price = price_current.find("strong")
        sup_price = price_current.find("sup")
        if strong_price is not None:
            return float(strong_price.text.replace(",","") + sup_price.text)
        else:
            return 0.0
    else:
        return 0.0

# function used to extract card shipping prices
def extract_shipping(cb):
    str_shipping = cb.find("li", class_ = "price-ship")
    if str_shipping is not None:
        shipping = str_shipping.text
        if shipping in ["Free Shipping", "Special Shipping", ""]:
            return 0.0
        else:
            return float(shipping.split(" ")[0].strip("$"))
    else:
        return 0.0

# function used to extract card image urls
def extract_img_url(cb):
    item_img = cb.find("a", class_ = "item-img")
    if item_img is not None:
        return item_img.find("img")["src"]
    else:
        return "NULL"

# function used to extract card features (max resolution, HDMI, DisplayPort, DirectX and model)
def extract_features(cb):
    all_features = cb.find("ul", class_ = "item-features")
    if all_features is not None:
        features = all_features.find_all('li')
        dict_of_features = {}
        for feature in features:
            split_text = feature.text.split(": ")
            if len(split_text) == 2:
                key, value = split_text
                if key == "Max Resolution" or key == "HDMI" or key == "DisplayPort" or key == "DirectX" or key == "Model #":
                    dict_of_features.update({key:value})
        return dict_of_features
    else:
        return "NULL"


#2. Define a function to extract all scraped data using functions above
rows = []

def process_card_blocks(soup):
    """Extract information from repeated divisions"""
    card_blocks = soup.find_all("div", class_="item-cell")
    for cb in card_blocks:
        row = extract_data(cb)
        rows.append(row)
        print(row)
                  
def extract_data(cb):
    title = extract_title(cb)
    brand = extract_brand(cb)
    itemid = extract_itemid(cb)
    rating = extract_rating(cb)
    num_ratings = extract_num_ratings(cb)
    price = extract_price(cb)
    shipping = extract_shipping(cb)
    img_url = extract_img_url(cb)
    features = extract_features(cb)
    
    row = dict(itemID = itemid,
               brand = brand,
               title = title,
               rating = rating,
               num_ratings = num_ratings,
               price = price,
               shipping = shipping,
               img_url = img_url,
               features = features)
    return row

#3. Loop through every web pages to scrape data
base_url = "https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48"
page_param = "/Page-"
tid_param = "?Tid=7709"
size_param = "&PageSize=36"

PAGES = []
for i in range(1, 101):
    url = base_url + page_param + str(i) + tid_param + size_param
    PAGES.append(url)

for PAGE in PAGES:
    result = requests.get(PAGE)
    source = result.text
    soup = BeautifulSoup(source, "html.parser")
    process_card_blocks(soup)

#4. Remove duplicate values before insert data to MySQL database
unique_rows = {d["title"]: d for d in rows}
unique_rows = list(unique_rows.values())

#5. Insert scraped data into a table in a MySQL database
engine = db.create_engine("mysql+mysqlconnector://root:password@localhost:3306/scraped_data")
connection = engine.connect()
insert_query = "INSERT INTO graphic_cards (itemID, title, brand, rating, num_ratings, price, shipping, img_url, features, total_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

for row in unique_rows:
        itemID_value = row.get("itemID")
        brand_value = row.get("brand")
        title_value = row.get("title")
        rating_value = row.get("rating")
        num_ratings_value = row.get("num_ratings")
        price_value = row.get("price")
        shipping_value = row.get("shipping")
        img_url_value = row.get("img_url")
        features_value = json.dumps(row.get("features"))
        total_price = price_value + shipping_value
        
        connection.execute(insert_query, (itemID_value, title_value, brand_value, rating_value, num_ratings_value, price_value, shipping_value, img_url_value, features_value, total_price))
