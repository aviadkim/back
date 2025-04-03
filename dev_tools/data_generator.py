#!/usr/bin/env python3
"""
Test Data Generator
------------------
This script generates realistic test data for your application,
including users, products, transactions, etc.

Usage:
1. Run in your GitHub Codespace
2. Customize the data types you need
3. Use the generated data to test your application
"""

import os
import uuid
import random
import argparse
import datetime
import csv
import json
from faker import Faker

class TestDataGenerator:
    def __init__(self):
        self.faker = Faker()
        self.data_types = {
            "users": self.generate_users,
            "products": self.generate_products,
            "orders": self.generate_orders,
            "transactions": self.generate_transactions,
            "posts": self.generate_posts,
            "comments": self.generate_comments
        }
    
    def generate_data(self, data_type, count=10, related_data=None):
        """Generate test data of the specified type"""
        if data_type not in self.data_types:
            print(f"Unknown data type: {data_type}")
            print(f"Available types: {', '.join(self.data_types.keys())}")
            return []
        
        print(f"Generating {count} {data_type}...")
        return self.data_types[data_type](count, related_data)
    
    def generate_users(self, count, _=None):
        """Generate user data"""
        users = []
        for _ in range(count):
            user_id = str(uuid.uuid4())
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            
            user = {
                "id": user_id,
                "firstName": first_name,
                "lastName": last_name,
                "email": self.faker.email(),
                "username": self.faker.user_name(),
                "password": "password123",  # Default password for test users
                "phone": self.faker.phone_number(),
                "address": {
                    "street": self.faker.street_address(),
                    "city": self.faker.city(),
                    "state": self.faker.state(),
                    "zipCode": self.faker.zipcode(),
                    "country": self.faker.country()
                },
                "createdAt": self.faker.date_time_this_year().isoformat(),
                "avatar": f"https://i.pravatar.cc/150?u={user_id}"
            }
            users.append(user)
        return users
    
    def generate_products(self, count, _=None):
        """Generate product data"""
        categories = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Sports", "Beauty", "Toys"]
        
        products = []
        for _ in range(count):
            product_id = str(uuid.uuid4())
            price = round(random.uniform(9.99, 999.99), 2)
            
            product = {
                "id": product_id,
                "name": self.faker.catch_phrase(),
                "description": self.faker.paragraph(),
                "price": price,
                "discountPercentage": random.choice([0, 5, 10, 15, 20]),
                "rating": round(random.uniform(1, 5), 1),
                "stock": random.randint(0, 100),
                "brand": self.faker.company(),
                "category": random.choice(categories),
                "thumbnail": f"https://picsum.photos/seed/{product_id}/200/300",
                "images": [
                    f"https://picsum.photos/seed/{product_id}-1/200/300",
                    f"https://picsum.photos/seed/{product_id}-2/200/300",
                ]
            }
            products.append(product)
        return products
    
    def generate_orders(self, count, related_data=None):
        """Generate order data"""
        users = related_data.get("users", []) if related_data else []
        products = related_data.get("products", []) if related_data else []
        
        if not users:
            users = self.generate_users(10)
        
        if not products:
            products = self.generate_products(20)
        
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        payment_methods = ["credit_card", "paypal", "bank_transfer", "cash_on_delivery"]
        
        orders = []
        for _ in range(count):
            order_id = str(uuid.uuid4())
            user = random.choice(users)
            
            # Generate 1-5 items per order
            items_count = random.randint(1, 5)
            order_products = random.sample(products, items_count)
            
            items = []
            total = 0
            
            for product in order_products:
                quantity = random.randint(1, 3)
                item_price = product["price"]
                item_total = item_price * quantity
                total += item_total
                
                items.append({
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "price": item_price,
                    "total": item_total
                })
            
            tax = round(total * 0.1, 2)
            shipping = round(random.uniform(5, 15), 2)
            grand_total = total + tax + shipping
            
            order_date = self.faker.date_time_this_year()
            
            order = {
                "id": order_id,
                "user_id": user["id"],
                "status": random.choice(statuses),
                "items": items,
                "subtotal": total,
                "tax": tax,
                "shipping": shipping,
                "total": grand_total,
                "payment_method": random.choice(payment_methods),
                "shipping_address": user["address"],
                "created_at": order_date.isoformat(),
                "updated_at": (order_date + datetime.timedelta(days=random.randint(1, 5))).isoformat()
            }
            orders.append(order)
        return orders
    
    def generate_transactions(self, count, related_data=None):
        """Generate transaction data"""
        users = related_data.get("users", []) if related_data else []
        
        if not users:
            users = self.generate_users(10)
        
        transaction_types = ["deposit", "withdrawal", "transfer", "payment", "refund"]
        statuses = ["pending", "completed", "failed", "reversed"]
        
        transactions = []
        for _ in range(count):
            transaction_id = str(uuid.uuid4())
            user = random.choice(users)
            
            amount = round(random.uniform(10, 1000), 2)
            transaction_type = random.choice(transaction_types)
            
            # For transfers, select a recipient
            recipient = None
            if transaction_type == "transfer":
                recipient = random.choice([u for u in users if u["id"] != user["id"]])
            
            transaction_date = self.faker.date_time_this_year()
            
            transaction = {
                "id": transaction_id,
                "user_id": user["id"],
                "type": transaction_type,
                "amount": amount,
                "status": random.choice(statuses),
                "created_at": transaction_date.isoformat(),
                "description": self.faker.sentence(),
                "reference": f"REF-{self.faker.bothify('??-####')}",
            }
            
            if recipient:
                transaction["recipient_id"] = recipient["id"]
                transaction["recipient_name"] = f"{recipient['firstName']} {recipient['lastName']}"
            
            transactions.append(transaction)
        return transactions
    
    def generate_posts(self, count, related_data=None):
        """Generate blog post data"""
        users = related_data.get("users", []) if related_data else []
        
        if not users:
            users = self.generate_users(5)
        
        categories = ["Technology", "Health", "Travel", "Food", "Business", "Entertainment"]
        
        posts = []
        for _ in range(count):
            post_id = str(uuid.uuid4())
            user = random.choice(users)
            
            paragraphs_count = random.randint(3, 7)
            paragraphs = [self.faker.paragraph() for _ in range(paragraphs_count)]
            content = "\n\n".join(paragraphs)
            
            tags = [self.faker.word() for _ in range(random.randint(2, 5))]
            
            post_date = self.faker.date_time_this_year()
            
            post = {
                "id": post_id,
                "title": self.faker.sentence(),
                "content": content,
                "author_id": user["id"],
                "author_name": f"{user['firstName']} {user['lastName']}",
                "category": random.choice(categories),
                "tags": tags,
                "image": f"https://picsum.photos/seed/{post_id}/800/600",
                "created_at": post_date.isoformat(),
                "updated_at": (post_date + datetime.timedelta(days=random.randint(0, 30))).isoformat(),
                "likes": random.randint(0, 100),
                "views": random.randint(10, 1000)
            }
            posts.append(post)
        return posts
    
    def generate_comments(self, count, related_data=None):
        """Generate comment data"""
        users = related_data.get("users", []) if related_data else []
        posts = related_data.get("posts", []) if related_data else []
        
        if not users:
            users = self.generate_users(10)
        
        if not posts:
            posts = self.generate_posts(5, {"users": users})
        
        comments = []
        for _ in range(count):
            comment_id = str(uuid.uuid4())
            user = random.choice(users)
            post = random.choice(posts)
            
            comment_date = self.faker.date_time_between(
                start_date=post["created_at"],
                end_date="now"
            )
            
            comment = {
                "id": comment_id,
                "post_id": post["id"],
                "user_id": user["id"],
                "user_name": f"{user['firstName']} {user['lastName']}",
                "content": self.faker.paragraph(),
                "created_at": comment_date.isoformat(),
                "likes": random.randint(0, 20)
            }
            comments.append(comment)
        return comments
    
    def save_data(self, data, data_type, format="json"):
        """Save generated data to file"""
        os.makedirs("test-data", exist_ok=True)
        
        if format == "json":
            filename = f"test-data/{data_type}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        elif format == "csv":
            filename = f"test-data/{data_type}.csv"
            if not data:
                print(f"No data to save for {data_type}")
                return
            
            # Flatten nested dictionaries for CSV
            flattened_data = []
            for item in data:
                flat_item = {}
                for key, value in item.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flat_item[f"{key}_{subkey}"] = subvalue
                    else:
                        flat_item[key] = value
                flattened_data.append(flat_item)
            
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        
        print(f"Saved {len(data)} {data_type} to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test data for your application")
    parser.add_argument("--type", choices=["users", "products", "orders", "transactions", "posts", "comments", "all"],
                        default="all", help="Type of data to generate")
    parser.add_argument("--count", type=int, default=10, help="Number of records to generate")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    generator = TestDataGenerator()
    
    if args.type == "all":
        # Generate all data types with relationships
        users = generator.generate_users(args.count)
        generator.save_data(users, "users", args.format)
        
        products = generator.generate_products(args.count * 2)
        generator.save_data(products, "products", args.format)
        
        related_data = {"users": users, "products": products}
        
        orders = generator.generate_orders(args.count, related_data)
        generator.save_data(orders, "orders", args.format)
        
        transactions = generator.generate_transactions(args.count, related_data)
        generator.save_data(transactions, "transactions", args.format)
        
        posts = generator.generate_posts(args.count, related_data)
        generator.save_data(posts, "posts", args.format)
        
        comments = generator.generate_comments(args.count * 3, {"users": users, "posts": posts})
        generator.save_data(comments, "comments", args.format)
    else:
        # Generate just the requested data type
        data = generator.generate_data(args.type, args.count)
        generator.save_data(data, args.type, args.format)