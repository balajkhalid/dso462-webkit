import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import gridfs
from bson import ObjectId
import os
from dotenv import load_dotenv

# Connect to MongoDB
load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))  # update URI as needed

db = client["web_kit_dso_462"] # replace with your DB name

fs = gridfs.GridFS(db)

# USER DATA

# Load the CSV into a DataFrame
user_df = pd.read_csv('data/users.csv')

# Convert DataFrame to dictionary format
user_data = user_df.to_dict(orient='records')

# Enter your desired collection name
user_collection = db["users"]  

# Insert the data
user_collection.insert_many(user_data)

print("Inserted users data successfully!")

# PRODUCTS 

# Load the CSV into a DataFrame
products_df = pd.read_csv('data/products.csv')

# Convert DataFrame to dictionary format
products_data = products_df.to_dict(orient='records')

image_dir = 'images/'

# Function to upload image file to GridFS
def upload_image(image_filename):
    with open(os.path.join(image_dir, image_filename), 'rb') as img_file:
        file_data = img_file.read()
    # Save image to GridFS
    file_id = fs.put(file_data, filename=image_filename)
    return file_id

# Insert Data into MongoDB and upload images
for product in products_data:
    image_filename = product["image"]
    file_id = upload_image(image_filename)
    product["image"] = file_id  # Store the file_id instead of the image path

# Enter your desired collection name
products_collection = db["products"]  

# Insert the data
products_collection.insert_many(products_data)

print("Inserted products data successfully!")


# USER PRODUCT INTERACTION DATA 

# Load the CSV into a DataFrame
interactions_df = pd.read_csv('data/user_product_interactions.csv')

# Convert DataFrame to dictionary format
interactions_data = interactions_df.to_dict(orient='records')

# Enter your desired collection name
interactions_collection = db["user_product_interactions"]  

# Insert the data
interactions_collection.insert_many(interactions_data)

print("Inserted users_product_interactions data successfully!")