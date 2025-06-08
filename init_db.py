import sqlite3
import os

if not os.path.exists("medicine.db"):
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()

    # Create users table
    c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Create bookmarks table
    c.execute('''
    CREATE TABLE bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_name TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

    print("✅ Database created successfully.")
else:
    print("📂 Database already exists.")
