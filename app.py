from flask import Flask, jsonify, send_from_directory, Response, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
import os
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from gridfs import GridFS
import re 
from dotenv import load_dotenv
import pickle
import numpy as np
from collections import Counter
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__, static_folder='static')
CORS(app)

# MongoDB Configuration

load_dotenv()
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
client = MongoClient(app.config["MONGO_URI"], server_api=ServerApi('1'))
db = client["web_kit_dso_462"]
collection = db["products"]
users_collection = db["users"]
fs = GridFS(db)

# RECOMMENDATION MODEL
# Load model and mappings
model = pickle.load(open("recommendation_model/model.pkl", "rb"))
user_ids = pickle.load(open("recommendation_model/user_ids.pkl", "rb"))
product_ids = pickle.load(open("recommendation_model/product_ids.pkl", "rb"))
product_lookup = pickle.load(open("recommendation_model/product_lookup.pkl", "rb"))
item_sim_matrix = pickle.load(open("recommendation_model/item_sim_matrix.pkl", "rb"))
item_features_matrix = sparse.load_npz("recommendation_model/item_features_matrix.npz")

item_embeddings = model.item_embeddings
item_sim_matrix = cosine_similarity(item_embeddings)

# Utility function to convert ObjectId to string
def mongo_to_dict(mongo_obj):
    mongo_obj["product_id"] = str(mongo_obj["product_id"]) 
    return mongo_obj

# Load initial file
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.errorhandler(404)
def page_not_found(error):
    return send_from_directory('static', '404.html'), 404

@app.route('/login')
def login():
    return send_from_directory('static', 'login.html')

@app.route('/login-form', methods=['POST'])
def login_form():
    print("in login form")
    data = request.get_json()

    email = data['email']
    password = data['password']
    user = users_collection.find_one({"email": email})
    
    if not user:
        print("no user")
        return jsonify({"error": "User not found. Please sign up!"}), 400

    # Validate password
    if not check_password_hash(user["password"], password):
        print("password error")
        return jsonify({"error": "Invalid password!"}), 400

    # Create session (if using sessions)
    # session["user_id"] = str(user["_id"])
    print("Login successful!")

    return jsonify({"message": "Login successful!"}), 200


@app.route('/signup')
def signup():
    return send_from_directory('static', 'signup.html')

@app.route('/signup-form', methods=['POST']) 
def signup_form():
    # Get the data from the incoming JSON
    data = request.get_json()

    username = data['fullname']
    dob = data['dob']
    email = data['email']
    password = data['password']
    confirm_password = data['confirm-password']

    # Check if the email is already taken
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists!"}), 400

    # Check if passwords match
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    # Check for strong password (minimum 8 characters, 1 uppercase, 1 lowercase, 1 digit)
    password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[A-Z]).{8,}$')
    if not password_pattern.match(password):
        return jsonify({"error": "Password must be at least 8 characters, with at least one uppercase letter, one lowercase letter, and one digit!"}), 400

    # Hash the password before saving
    hashed_password = generate_password_hash(password)

    # Create user document
    user_data = {
        "username": username,
        "dob": dob,
        "email": email,
        "password": hashed_password
    }

    # Insert user data into MongoDB
    try:
        users_collection.insert_one(user_data)
        return jsonify({"message": "Account created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/best-sellers', methods=['GET'])
def get_best_sellers():
    products = collection.find()
    product_list = [
        mongo_to_dict({
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "image": f"/image/{str(product['image'])}",
            "product_id": product["product_id"]
        })
        for product in products
    ]
    return jsonify(product_list)

@app.route('/product')
def product_page():
    return send_from_directory('static', 'product.html')

@app.route('/products-details', methods=['GET'])
def get_product_details():
    try:
        product_id = request.args.get("productId")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing product_id"}), 400

    product_details = collection.find_one({"product_id": product_id})
    if not product_details:
        print("No Product Details Found")
        return jsonify({"error": "Product not found."}), 400
    product_details_json = mongo_to_dict({
        "name": product_details["name"],
        "description": product_details["description"],
        "price": product_details["price"],
        "image": f"/image/{str(product_details['image'])}",
        "product_id": product_details["product_id"]
    })
    return jsonify(product_details_json)

@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        # Fetch image from GridFS using the ObjectId
        image_id = ObjectId(image_id)  # Convert string back to ObjectId
        file = fs.get(image_id)  # Get the file from GridFS
        
        # Detect the MIME type based on the file extension or header (you may use python-magic for this)
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension == 'jpg' or file_extension == 'jpeg':
            mimetype = 'image/jpeg'
        elif file_extension == 'png':
            mimetype = 'image/png'
        else:
            mimetype = 'application/octet-stream'  # Default MIME type for unknown files

        return Response(file.read(), mimetype=mimetype)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# RECOMMENDATION MODEL

def get_similar_products(product_id, top_n=5):
    if product_id not in product_ids:
        print(f"Product {product_id} not found. Showing popular items instead.")
        return get_fallback_recommendations(top_n)

    product_idx = product_ids.index(product_id)
    sim_scores = item_sim_matrix[product_idx]
    
    # Exclude the product itself
    similar_indices = np.argsort(-sim_scores)
    similar_indices = [i for i in similar_indices if product_ids[i] != product_id][:top_n]
    
    similar_product_ids = [product_ids[i] for i in similar_indices]
    return similar_product_ids

def get_fallback_recommendations(top_n=5):
    interactions = list(db["user_product_interactions"].find())
    product_counts = Counter(i['product_id'] for i in interactions)
    
    # Most interacted product_ids
    top_product_ids = [pid for pid, _ in product_counts.most_common(top_n)]
    
    print("Fallback (popular) recommendations:")
    for pid in top_product_ids:
        print(f"  {product_lookup[pid]['name']}")
    
    return top_product_ids

def recommend(user_id, model, user_ids, product_id=None, top_n=5):
    if user_id not in user_ids:
        print(f"User {user_id} not found in training data.")
        if product_id:
            return get_similar_products(product_id, top_n)
        return get_fallback_recommendations(top_n)

    user_index = user_ids.index(user_id)
    scores = model.predict(user_index, np.arange(len(product_ids)), item_features=item_features_matrix)

    # Boost similarity if product_id is provided
    if product_id and product_id in product_ids:
        current_idx = product_ids.index(product_id)
        similarity_boost = item_sim_matrix[current_idx]
        if similarity_boost.shape == scores.shape:
            scores += 0.25 * similarity_boost  # Tune this boost factor as needed

    top_items = np.argsort(-scores)
    seen = set()
    top_product_ids = []
    for i in top_items:
        pid = product_ids[i]
        if pid != product_id and pid not in seen:
            top_product_ids.append(pid)
            seen.add(pid)
        if len(top_product_ids) == top_n:
            break

    return top_product_ids

@app.route('/similar-products', methods=['GET'])
def similar_products_api():
    product_id = request.args.get("productId")
    user_id = int(request.args.get("userId"))

    recommended_ids = recommend(user_id, model, user_ids, product_id=product_id)

    similar_products = []
    for pid in recommended_ids:
        product = collection.find_one({"product_id": pid})
        if product:
            similar_products.append(mongo_to_dict({
                "name": product["name"],
                "price": product["price"],
                "image": f"/image/{str(product['image'])}",
                "product_id": product["product_id"]
            }))

    return jsonify(similar_products)


if __name__ == '__main__':
    app.run(debug=True)