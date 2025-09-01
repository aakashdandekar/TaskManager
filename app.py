from flask import *
import sqlite3
import json

app = Flask(__name__)

DB_FILE = "users.db"
SIGNUP_KEY = "ABC123"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            tasks TEXT DEFAULT '[]'
        )
    ''')
    cursor.execute('SELECT username FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (username, password, tasks) VALUES (?, ?, ?)', 
                      ('admin', '2006', '[]'))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT username, password, tasks FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'username': user[0], 'password': user[1], 'tasks': json.loads(user[2])}
    return None

def create_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, tasks) VALUES (?, ?, ?)', 
                  (username, password, '[]'))
    conn.commit()
    conn.close()

def update_user_tasks(username, tasks):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET tasks = ? WHERE username = ?', 
                  (json.dumps(tasks), username))
    conn.commit()
    conn.close()

def update_user_password(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', 
                  (password, username))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT username, tasks FROM users WHERE username != ?', ('admin',))
    users = cursor.fetchall()
    conn.close()
    return [{'username': user[0], 'tasks': len(json.loads(user[1]))} for user in users]

def delete_user_db(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return redirect("/login")

@app.errorhandler(404)
def not_found(error):
    return "404 - Page Not Found", 404

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    data = request.json
    username = data.get("username")
    password = data.get("password")
    signup_key = data.get("signup_key")

    if signup_key != SIGNUP_KEY:
        return jsonify({"error": "Invalid signup key!"}), 400

    if get_user(username):
        return jsonify({"error": "User already exists!"}), 400

    create_user(username, password)
    return jsonify({"message": "User created successfully!"}), 201

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = get_user(username)
    if not user or user['password'] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": f"Welcome {username}!"}), 200

@app.route("/add_data", methods=["POST"])
def add_data():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    new_item = data.get("item")

    user = get_user(username)
    if not user or user['password'] != password:
        return jsonify({"error": "Authentication failed"}), 401

    if isinstance(new_item, list):
        tasks = new_item
    else:
        tasks = user['tasks']
        tasks.append(new_item)
    
    update_user_tasks(username, tasks)
    return jsonify({"message": "Data added", "data": tasks})

@app.route("/view_data", methods=["POST"])
def view_data():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = get_user(username)
    if not user or user['password'] != password:
        return jsonify({"error": "Authentication failed"}), 401

    return jsonify({"data": user['tasks']})

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if request.method == "GET":
        return render_template("admin.html")
    
    data = request.json
    username = data.get("username")
    password = data.get("password")
    new_signup_key = data.get("new_signup_key")
    
    admin_user = get_user('admin')
    if username != "admin" or password != admin_user['password']:
        return jsonify({"error": "Admin access required!"}), 401
    
    if len(new_signup_key) != 6 or not new_signup_key.isupper() or not new_signup_key.isalnum():
        return jsonify({"error": "Signup key must be 6 characters, uppercase letters and numbers only!"}), 400
    
    global SIGNUP_KEY
    SIGNUP_KEY = new_signup_key
    return jsonify({"message": f"Signup key updated to: {SIGNUP_KEY}"}), 200

@app.route("/get_users", methods=["POST"])
def get_users():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    admin_user = get_user('admin')
    if username != "admin" or password != admin_user['password']:
        return jsonify({"error": "Admin access required!"}), 401
    
    user_list = get_all_users()
    return jsonify({"users": user_list}), 200

@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.json
    admin_username = data.get("username")
    admin_password = data.get("password")
    target_user = data.get("target_user")
    
    admin_user = get_user('admin')
    if admin_username != "admin" or admin_password != admin_user['password']:
        return jsonify({"error": "Admin access required!"}), 401
    
    if target_user == "admin":
        return jsonify({"error": "Cannot delete admin account!"}), 400
    
    if get_user(target_user):
        delete_user_db(target_user)
        return jsonify({"message": f"User {target_user} deleted successfully!"}), 200
    else:
        return jsonify({"error": "User not found!"}), 404

@app.route("/update_password", methods=["POST"])
def update_password():
    data = request.json
    username = data.get("username")
    new_password = data.get("new_password")
    
    if not get_user(username):
        return jsonify({"error": "User not found!"}), 404
    
    update_user_password(username, new_password)
    return jsonify({"message": "Password updated successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)