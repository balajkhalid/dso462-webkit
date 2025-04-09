import pandas as pd
from lightfm import LightFM
from lightfm.data import Dataset
import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import pickle
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables and connect to MongoDB
load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["web_kit_dso_462"]

# Load data (update collection names)
users = list(db["users"].find()) 
products = list(db["products"].find())
interactions = list(db["user_product_interactions"].find())

user_ids = [u['user_id'] for u in users]
product_ids = [p['product_id'] for p in products]

# Create product lookup for later use
product_lookup = {p['product_id']: p for p in products}

# Initialize dataset
dataset = Dataset()
dataset.fit(user_ids, product_ids)

# Add user features
user_features_list = [(u['user_id'], [u['city']]) for u in users]
dataset.fit_partial(users=user_ids, user_features=[u['city'] for u in users])
user_features_matrix = dataset.build_user_features(user_features_list)

# Add item features
item_features_list = [(p['product_id'], [p['category']]) for p in products]
dataset.fit_partial(items=product_ids, item_features=[p['category'] for p in products])
item_features_matrix = dataset.build_item_features(item_features_list)

# Build interactions
interactions_list = [(i['user_id'], i['product_id']) for i in interactions]
(interactions_matrix, _) = dataset.build_interactions(interactions_list)

# Train model
model = LightFM(loss='warp')
model.fit(interactions_matrix, user_features=user_features_matrix, item_features=item_features_matrix, epochs=10)

# Compute item similarity matrix
item_embeddings = model.item_embeddings
item_sim_matrix = cosine_similarity(item_embeddings)

# Save everything
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("user_ids.pkl", "wb") as f:
    pickle.dump(user_ids, f)
with open("product_ids.pkl", "wb") as f:
    pickle.dump(product_ids, f)
with open("product_lookup.pkl", "wb") as f:
    pickle.dump(product_lookup, f)
with open("item_sim_matrix.pkl", "wb") as f:
    pickle.dump(item_sim_matrix, f)
sparse.save_npz("item_features_matrix.npz", item_features_matrix)

print("✅ Model, features, and similarity matrix saved successfully.")