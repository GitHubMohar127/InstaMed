from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import requests
from io import BytesIO
import base64
import os

app = Flask(__name__)
app.secret_key = 'mohar-medicine-app-2004'  # Use an environment variable in production

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -----------------------------
# Flask-Login User Class
# -----------------------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

# -----------------------------
# Register Route
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect("medicine.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Account created! Please log in.')
            return redirect(url_for('login'))
        except:
            flash('Username already exists.')
        finally:
            conn.close()
    return render_template('register.html')

# -----------------------------
# Login Route
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("medicine.db")
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            user_obj = User(user[0], username)
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

# -----------------------------
# Logout Route
# -----------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -----------------------------
# Bookmark Routes
# -----------------------------
@app.route('/bookmark', methods=['POST'])
@login_required
def bookmark():
    medicine_name = request.form['medicine_name']
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()
    c.execute("INSERT INTO bookmarks (user_id, medicine_name) VALUES (?, ?)", (current_user.id, medicine_name))
    conn.commit()
    conn.close()
    flash("\ud83d\udd16 Medicine bookmarked!")
    return redirect(url_for('index'))

@app.route('/bookmarks')
@login_required
def show_bookmarks():
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()
    c.execute("SELECT medicine_name FROM bookmarks WHERE user_id=?", (current_user.id,))
    bookmarks = c.fetchall()
    conn.close()
    return render_template('bookmarks.html', bookmarks=bookmarks)

# -----------------------------
# Load CSV Data Once
# -----------------------------
df = pd.read_csv("Medicine_Details.csv")

# -----------------------------
# Home Route (Search & Display)
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
@login_required

def index():
    medicine_info = None
    image_data = None
    error_msg = None

    if request.method == 'POST':
        medicine_name = request.form.get('medicine_name', '').strip().lower()
        filtered_data = df[df['Medicine Name'].str.lower().str.contains(medicine_name)]

        if filtered_data.empty:
            error_msg = "\u274c No medicine found with that name."
        else:
            selected = filtered_data.iloc[0]
            medicine_info = {
                "Uses": selected.get("Uses", "N/A"),
                "Medicine Name": selected.get("Medicine Name", "N/A"),
                "Composition": selected.get("Composition", "N/A"),
                "Side Effects": selected.get("Side_effects", "N/A"),
                "Manufacturer": selected.get("Manufacturer", "N/A"),
                "Average Review": selected.get("Average Review %", "N/A")
            }

            try:
                response = requests.get(selected["Image URL"], timeout=5)
                img_bytes = BytesIO(response.content).getvalue()
                image_data = base64.b64encode(img_bytes).decode('utf-8')
            except Exception as e:
                image_data = None
                error_msg = f"\u26a0 Failed to load image: {e}"

    return render_template('index.html', medicine_info=medicine_info, image_data=image_data, error_msg=error_msg)

# -----------------------------
# AJAX Suggestion Route
# -----------------------------
@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    suggestions = df[df['Medicine Name'].str.lower().str.contains(query)]
    suggestions_list = suggestions['Medicine Name'].drop_duplicates().head(10).tolist()
    return jsonify(suggestions_list)

# -----------------------------
# Run Server
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
