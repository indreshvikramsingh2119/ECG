import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            local_id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            age TEXT,
            gender TEXT,
            address TEXT,
            profile_pic TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user(local_id, email, name, phone="", age="", gender="", address="", profile_pic="", password=""):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO users (local_id, email, name, phone, age, gender, address, profile_pic, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (local_id, email, name, phone, age, gender, address, profile_pic, password))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def validate_user(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    return user