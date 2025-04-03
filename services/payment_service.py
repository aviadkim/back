import os
import hmac
import hashlib
from flask import request, jsonify
from functools import wraps
from config import Config

class PaymentService:
    def __init__(self):
        self.paddle_vendor_id = os.getenv('PADDLE_VENDOR_ID')
        self.paddle_api_key = os.getenv('PADDLE_API_KEY')
        self.paddle_public_key = os.getenv('PADDLE_PUBLIC_KEY')
        
    def verify_webhook(self, data, signature):
        """Verify Paddle webhook signature"""
        public_key = Config.PADDLE_PUBLIC_KEY
        signed_payload = f"{data['p_signature']}|{data['alert_name']}|{data['alert_id']}"
        return hmac.compare_digest(
            signature,
            hmac.new(public_key.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
        )

    def create_subscription(self, user_id, plan_id):
        """Create a new subscription"""
        # Implementation will call Paddle API
        pass

    def cancel_subscription(self, subscription_id):
        """Cancel an existing subscription"""
        # Implementation will call Paddle API
        pass

    def webhook_handler(self, f):
        """Decorator for Paddle webhook handlers"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            signature = request.headers.get('Paddle-Signature')
            if not self.verify_webhook(request.json, signature):
                return jsonify({"error": "Invalid signature"}), 403
            return f(*args, **kwargs)
        return wrapper