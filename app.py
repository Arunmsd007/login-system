# app.py
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pymongo
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import certifi
from bson import ObjectId
from functools import wraps
import pytz

# --- Initialization ---
load_dotenv()
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- Configuration ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-strong-secret-key-for-dev')
MONGO_URI = os.environ.get('MONGO_URI')

if not MONGO_URI:
    raise ValueError("MONGO_URI not found. Please check your .env file.")

IST = pytz.timezone('Asia/Kolkata')

# --- Database Connection ---
try:
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database()
    users_collection = db.users
    sessions_collection = db.sessions
    print("✅ MongoDB connection successful.")
except Exception as e:
    print(f"❌ Failed to connect to the database: {e}")
    client = None

# --- JWT Decorator for Admin Routes ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = users_collection.find_one({'username': data['username']})
            if not current_user or current_user.get('role') != 'admin':
                return jsonify({'error': 'Admin privileges required'}), 403
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'error': 'Token is invalid or expired'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- API Endpoints ---

@app.route('/register', methods=['POST'])
def register():
    if not client: return jsonify({"error": "Database connection failed"}), 500
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    if not username or not password: return jsonify({"error": "Username and password required"}), 400
    if users_collection.find_one({"username": username}): return jsonify({"error": "Username already exists"}), 409
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed_password, "role": "user"})
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    if not client: return jsonify({"error": "Database connection failed"}), 500
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session_id = sessions_collection.insert_one({
            'username': username, 'login_time': datetime.now(timezone.utc), 'logout_time': None
        }).inserted_id
        token = jwt.encode({
            'username': username, 'role': user.get('role', 'user'),
            'session_id': str(session_id),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    session_id = data.get('session_id')
    if session_id:
        try:
            sessions_collection.update_one(
                {'_id': ObjectId(session_id)}, {'$set': {'logout_time': datetime.now(timezone.utc)}}
            )
        except Exception:
            # Fails silently if session_id is invalid, which is acceptable for logout
            pass
    return jsonify({"message": "Logout successful"}), 200

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    username, new_password = data.get('username'), data.get('new_password')
    if not username or not new_password:
        return jsonify({'error': 'Username and new password are required'}), 400
    user = users_collection.find_one({'username': username})
    if not user: return jsonify({'error': 'Username not found'}), 404
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    users_collection.update_one({'username': username}, {'$set': {'password': hashed_password}})
    return jsonify({'message': 'Password has been reset successfully'}), 200

@app.route('/admin/dashboard', methods=['GET'])
@token_required
def admin_dashboard(current_user):
    sessions = list(sessions_collection.find().sort("login_time", -1))
    processed_sessions = []
    for session in sessions:
        login_time_utc = session['login_time'].replace(tzinfo=pytz.utc)
        login_time_ist = login_time_utc.astimezone(IST)
        logout_time_ist_str = "Active"
        if session.get('logout_time'):
            logout_time_utc = session['logout_time'].replace(tzinfo=pytz.utc)
            logout_time_ist = logout_time_utc.astimezone(IST)
            logout_time_ist_str = logout_time_ist.strftime('%d/%m/%Y, %I:%M:%S %p')
        processed_sessions.append({
            "_id": str(session['_id']), "username": session['username'],
            "login_time_ist": login_time_ist.strftime('%d/%m/%Y, %I:%M:%S %p'),
            "logout_time_ist": logout_time_ist_str
        })
    return jsonify(processed_sessions)

@app.route('/admin/session/<session_id>', methods=['DELETE'])
@token_required
def delete_session(current_user, session_id):
    try:
        result = sessions_collection.delete_one({'_id': ObjectId(session_id)})
        if result.deleted_count == 1:
            return jsonify({'message': 'Session deleted successfully'}), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500

# --- Serving the Frontend ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

