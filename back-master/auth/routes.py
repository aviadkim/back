
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import re
import os
from functools import wraps

from auth import auth_bp
from mongodb.connection import get_db_collections

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get MongoDB collections
db, collections = get_db_collections()
users_collection = collections['users']

# JWT configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'development_secret_key')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = users_collection.find_one({'_id': data['user_id']})
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if username exists
    if users_collection.find_one({'username': data['username']}):
        return jsonify({'error': 'Username already taken'}), 400
    
    # Check if email exists
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'created_at': datetime.now(),
        'last_login': None,
        'role': 'user',
        'organization': data.get('organization', ''),
        'settings': {},
        'subscription': {
            'plan': 'free',
            'status': 'active',
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=30),
            'features': ['basic_analysis']
        }
    }
    
    # Insert user
    result = users_collection.insert_one(new_user)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(result.inserted_id)
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    data = request.get_json()
    
    # Check for email/username and password
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email/username or password'}), 400
    
    # Find user by email
    user = users_collection.find_one({'email': data['email']})
    
    # If not found by email, try username
    if not user and 'username' in data:
        user = users_collection.find_one({'username': data['username']})
    
    # Check user exists and password is correct
    if not user or not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token_expiration = datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
    token = jwt.encode(
        {
            'user_id': str(user['_id']),
            'exp': token_expiration
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    
    # Update last login
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'last_login': datetime.now()}}
    )
    
    return jsonify({
        'token': token,
        'expires_at': token_expiration.isoformat(),
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'organization': user['organization']
        }
    })

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify({
        'id': str(current_user['_id']),
        'username': current_user['username'],
        'email': current_user['email'],
        'role': current_user['role'],
        'organization': current_user['organization'],
        'created_at': current_user['created_at'].isoformat() if isinstance(current_user['created_at'], datetime) else current_user['created_at'],
        'last_login': current_user['last_login'].isoformat() if current_user['last_login'] and isinstance(current_user['last_login'], datetime) else current_user['last_login'],
        'subscription': current_user.get('subscription', {})
    })

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users (admin only)"""
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = []
    for user in users_collection.find():
        users.append({
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'organization': user['organization'],
            'created_at': user['created_at'].isoformat() if isinstance(user['created_at'], datetime) else user['created_at'],
            'last_login': user['last_login'].isoformat() if user['last_login'] and isinstance(user['last_login'], datetime) else user['last_login']
        })
    
    return jsonify({'users': users})
