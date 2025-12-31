"""
ĐỀ BÀI: AGENTIC CODING - REFACTOR SPAGHETTI CODE
=================================================
Bối cảnh: Đây là hệ thống xử lý đơn hàng e-commerce được viết bởi một junior developer
trong 1 đêm để kịp deadline. Code hoạt động nhưng không thể maintain được.

YÊU CẦU:
1. Viết các prompt để Agent phân tách code thành các module riêng biệt tuân thủ theo quy trình SDD trong khoá học
2. Áp dụng Design Pattern phù hợp
3. Tự động generate Unit Tests với coverage >= 80%
4. Giải thích quy trình và các prompts đã sử dụng
"""

import sqlite3
import json
import hashlib
import smtplib
from datetime import datetime
import random
import string

# Global variables - BAD PRACTICE
db = None
email_server = None
TAX_RATE = 0.1
DISCOUNT_CODES = {"SAVE10": 10, "SAVE20": 20, "VIP50": 50, "FREESHIP": 0}
current_user = None
order_counter = 1000
logs = []

class EcommerceSystem:
    def __init__(self):
        global db, email_server, order_counter
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT, role TEXT, balance REAL, created_at TEXT)")
        db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, category TEXT)")
        db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, items TEXT, total REAL, status TEXT, created_at TEXT, shipping_address TEXT)")
        db.execute("CREATE TABLE reviews (id INTEGER PRIMARY KEY, product_id INTEGER, user_id INTEGER, rating INTEGER, comment TEXT)")
        db.execute("CREATE TABLE coupons (code TEXT PRIMARY KEY, discount INTEGER, used INTEGER, max_uses INTEGER)")
        db.commit()
        for code, discount in DISCOUNT_CODES.items():
            db.execute("INSERT INTO coupons VALUES (?, ?, 0, 100)", (code, discount))
        db.commit()
        email_server = {"host": "smtp.fake.com", "port": 587}
        order_counter = 1000
        
    def do_everything(self, action, data=None):
        global current_user, order_counter, logs
        
        if action == "register":
            if data.get("name") and data.get("email") and data.get("password"):
                if len(data["password"]) < 6:
                    return {"error": "Password too short"}
                if "@" not in data["email"]:
                    return {"error": "Invalid email"}
                existing = db.execute("SELECT * FROM users WHERE email = ?", (data["email"],)).fetchone()
                if existing:
                    return {"error": "Email exists"}
                hashed = hashlib.md5(data["password"].encode()).hexdigest()
                db.execute("INSERT INTO users (name, email, password, role, balance, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                          (data["name"], data["email"], hashed, "customer", 0.0, datetime.now().isoformat()))
                db.commit()
                logs.append(f"[{datetime.now()}] User registered: {data['email']}")
                # Send welcome email
                try:
                    msg = f"Welcome {data['name']}! Thanks for joining our platform."
                    print(f"EMAIL SENT to {data['email']}: {msg}")
                except:
                    pass
                return {"success": True, "message": "Registered successfully"}
            else:
                return {"error": "Missing fields"}
                
        elif action == "login":
            if data.get("email") and data.get("password"):
                hashed = hashlib.md5(data["password"].encode()).hexdigest()
                user = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                                 (data["email"], hashed)).fetchone()
                if user:
                    current_user = {"id": user[0], "name": user[1], "email": user[2], "role": user[4], "balance": user[5]}
                    logs.append(f"[{datetime.now()}] User logged in: {data['email']}")
                    return {"success": True, "user": current_user}
                else:
                    return {"error": "Invalid credentials"}
            return {"error": "Missing fields"}
            
        elif action == "add_product":
            if current_user and current_user["role"] == "admin":
                if data.get("name") and data.get("price") and data.get("stock"):
                    if data["price"] <= 0:
                        return {"error": "Invalid price"}
                    if data["stock"] < 0:
                        return {"error": "Invalid stock"}
                    db.execute("INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)",
                              (data["name"], data["price"], data["stock"], data.get("category", "general")))
                    db.commit()
                    logs.append(f"[{datetime.now()}] Product added: {data['name']}")
                    return {"success": True}
                return {"error": "Missing fields"}
            return {"error": "Unauthorized"}
            
        elif action == "get_products":
            products = db.execute("SELECT * FROM products").fetchall()
            result = []
            for p in products:
                result.append({"id": p[0], "name": p[1], "price": p[2], "stock": p[3], "category": p[4]})
            return {"products": result}
            
        elif action == "search_products":
            if data.get("query"):
                products = db.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", 
                                     (f"%{data['query']}%", f"%{data['query']}%")).fetchall()
                result = []
                for p in products:
                    result.append({"id": p[0], "name": p[1], "price": p[2], "stock": p[3], "category": p[4]})
                return {"products": result}
            return {"products": []}
            
        elif action == "create_order":
            if not current_user:
                return {"error": "Not logged in"}
            if not data.get("items"):
                return {"error": "No items"}
            if not data.get("shipping_address"):
                return {"error": "No shipping address"}
                
            total = 0
            order_items = []
            for item in data["items"]:
                product = db.execute("SELECT * FROM products WHERE id = ?", (item["product_id"],)).fetchone()
                if not product:
                    return {"error": f"Product {item['product_id']} not found"}
                if product[3] < item["quantity"]:
                    return {"error": f"Not enough stock for {product[1]}"}
                item_total = product[2] * item["quantity"]
                total += item_total
                order_items.append({"product_id": product[0], "name": product[1], "price": product[2], 
                                   "quantity": item["quantity"], "subtotal": item_total})
                # Update stock
                db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))
            
            # Apply discount
            discount_amount = 0
            if data.get("coupon_code"):
                coupon = db.execute("SELECT * FROM coupons WHERE code = ?", (data["coupon_code"],)).fetchone()
                if coupon:
                    if coupon[2] < coupon[3]:  # used < max_uses
                        discount_amount = total * (coupon[1] / 100)
                        db.execute("UPDATE coupons SET used = used + 1 WHERE code = ?", (data["coupon_code"],))
                    else:
                        return {"error": "Coupon expired"}
                else:
                    return {"error": "Invalid coupon"}
            
            # Calculate tax
            tax = (total - discount_amount) * TAX_RATE
            final_total = total - discount_amount + tax
            
            # Check balance for VIP users
            if current_user["role"] == "vip":
                if current_user["balance"] >= final_total:
                    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", 
                              (final_total, current_user["id"]))
                    payment_status = "paid_with_balance"
                else:
                    payment_status = "pending_payment"
            else:
                payment_status = "pending_payment"
            
            order_counter += 1
            order_id = order_counter
            db.execute("INSERT INTO orders (id, user_id, items, total, status, created_at, shipping_address) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (order_id, current_user["id"], json.dumps(order_items), final_total, payment_status, 
                       datetime.now().isoformat(), data["shipping_address"]))
            db.commit()
            
            logs.append(f"[{datetime.now()}] Order created: #{order_id} by user {current_user['id']}")
            
            # Send order confirmation email
            try:
                msg = f"Order #{order_id} confirmed! Total: ${final_total:.2f}"
                print(f"EMAIL SENT to {current_user['email']}: {msg}")
            except:
                pass
            
            return {"success": True, "order_id": order_id, "total": final_total, "status": payment_status,
                   "breakdown": {"subtotal": total, "discount": discount_amount, "tax": tax}}
                   
        elif action == "get_orders":
            if not current_user:
                return {"error": "Not logged in"}
            if current_user["role"] == "admin":
                orders = db.execute("SELECT * FROM orders").fetchall()
            else:
                orders = db.execute("SELECT * FROM orders WHERE user_id = ?", (current_user["id"],)).fetchall()
            result = []
            for o in orders:
                result.append({"id": o[0], "user_id": o[1], "items": json.loads(o[2]), "total": o[3], 
                              "status": o[4], "created_at": o[5], "shipping_address": o[6]})
            return {"orders": result}
            
        elif action == "update_order_status":
            if not current_user or current_user["role"] != "admin":
                return {"error": "Unauthorized"}
            if data.get("order_id") and data.get("status"):
                if data["status"] not in ["pending_payment", "paid", "processing", "shipped", "delivered", "cancelled"]:
                    return {"error": "Invalid status"}
                db.execute("UPDATE orders SET status = ? WHERE id = ?", (data["status"], data["order_id"]))
                db.commit()
                # Get order details for notification
                order = db.execute("SELECT * FROM orders WHERE id = ?", (data["order_id"],)).fetchone()
                if order:
                    user = db.execute("SELECT * FROM users WHERE id = ?", (order[1],)).fetchone()
                    if user:
                        try:
                            msg = f"Your order #{data['order_id']} status updated to: {data['status']}"
                            print(f"EMAIL SENT to {user[2]}: {msg}")
                        except:
                            pass
                logs.append(f"[{datetime.now()}] Order #{data['order_id']} status updated to {data['status']}")
                return {"success": True}
            return {"error": "Missing fields"}
            
        elif action == "add_review":
            if not current_user:
                return {"error": "Not logged in"}
            if data.get("product_id") and data.get("rating") and data.get("comment"):
                if data["rating"] < 1 or data["rating"] > 5:
                    return {"error": "Rating must be 1-5"}
                # Check if user purchased this product
                orders = db.execute("SELECT * FROM orders WHERE user_id = ?", (current_user["id"],)).fetchall()
                purchased = False
                for order in orders:
                    items = json.loads(order[2])
                    for item in items:
                        if item["product_id"] == data["product_id"]:
                            purchased = True
                            break
                if not purchased:
                    return {"error": "You must purchase the product first"}
                db.execute("INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
                          (data["product_id"], current_user["id"], data["rating"], data["comment"]))
                db.commit()
                return {"success": True}
            return {"error": "Missing fields"}
            
        elif action == "get_reviews":
            if data.get("product_id"):
                reviews = db.execute("SELECT r.*, u.name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = ?",
                                    (data["product_id"],)).fetchone()
                if reviews:
                    return {"reviews": [{"id": reviews[0], "rating": reviews[3], "comment": reviews[4], "user": reviews[5]}]}
            return {"reviews": []}
            
        elif action == "get_analytics":
            if not current_user or current_user["role"] != "admin":
                return {"error": "Unauthorized"}
            total_orders = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            total_revenue = db.execute("SELECT SUM(total) FROM orders WHERE status != 'cancelled'").fetchone()[0] or 0
            total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            top_products = db.execute("""
                SELECT p.name, SUM(json_extract(o.items, '$[0].quantity')) as qty 
                FROM orders o, products p 
                WHERE o.status != 'cancelled' 
                GROUP BY p.name 
                ORDER BY qty DESC LIMIT 5
            """).fetchall()
            return {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "total_users": total_users,
                "top_products": [{"name": p[0], "sold": p[1]} for p in top_products]
            }
            
        elif action == "generate_report":
            if not current_user or current_user["role"] != "admin":
                return {"error": "Unauthorized"}
            report = f"""
            ===================== SALES REPORT =====================
            Generated: {datetime.now().isoformat()}
            
            Total Orders: {db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]}
            Total Revenue: ${db.execute("SELECT SUM(total) FROM orders WHERE status != 'cancelled'").fetchone()[0] or 0:.2f}
            Pending Orders: {db.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending_payment'").fetchone()[0]}
            Shipped Orders: {db.execute("SELECT COUNT(*) FROM orders WHERE status = 'shipped'").fetchone()[0]}
            
            ===================== END REPORT =====================
            """
            return {"report": report}
            
        elif action == "add_balance":
            if not current_user or current_user["role"] != "admin":
                return {"error": "Unauthorized"}
            if data.get("user_id") and data.get("amount"):
                if data["amount"] <= 0:
                    return {"error": "Invalid amount"}
                db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (data["amount"], data["user_id"]))
                db.commit()
                logs.append(f"[{datetime.now()}] Balance added: ${data['amount']} to user {data['user_id']}")
                return {"success": True}
            return {"error": "Missing fields"}
            
        elif action == "get_logs":
            if not current_user or current_user["role"] != "admin":
                return {"error": "Unauthorized"}
            return {"logs": logs[-50:]}  # Last 50 logs
            
        else:
            return {"error": "Unknown action"}


# Test the spaghetti code
if __name__ == "__main__":
    system = EcommerceSystem()
    
    # Register admin
    print(system.do_everything("register", {"name": "Admin", "email": "admin@test.com", "password": "admin123"}))
    
    # Login as admin (manually set role for testing)
    db.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@test.com'")
    db.commit()
    print(system.do_everything("login", {"email": "admin@test.com", "password": "admin123"}))
    
    # Add products
    print(system.do_everything("add_product", {"name": "Laptop", "price": 999.99, "stock": 10, "category": "electronics"}))
    print(system.do_everything("add_product", {"name": "Mouse", "price": 29.99, "stock": 100, "category": "electronics"}))
    print(system.do_everything("add_product", {"name": "Keyboard", "price": 79.99, "stock": 50, "category": "electronics"}))
    
    # Register customer
    print(system.do_everything("register", {"name": "John", "email": "john@test.com", "password": "john123"}))
    print(system.do_everything("login", {"email": "john@test.com", "password": "john123"}))
    
    # Get products
    print(system.do_everything("get_products"))
    
    # Create order
    print(system.do_everything("create_order", {
        "items": [{"product_id": 1, "quantity": 1}, {"product_id": 2, "quantity": 2}],
        "shipping_address": "123 Main St",
        "coupon_code": "SAVE10"
    }))
    
    # Get orders
    print(system.do_everything("get_orders"))
