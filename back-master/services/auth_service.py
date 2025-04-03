import os
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from config import Config

class AuthService:
    def __init__(self):
        self.secret_key = Config.SECRET_KEY
        self.jwt_secret = Config.JWT_SECRET

    def generate_token(self, user_id):
        """Generate JWT token"""
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                self.jwt_secret,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def verify_token(self, auth_token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(auth_token, self.jwt_secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def hash_password(self, password):
        """Hash a password for storing"""
        return generate_password_hash(password)

    def verify_password(self, stored_hash, provided_password):
        """Verify a stored password against one provided by user"""
        return check_password_hash(stored_hash, provided_password)