import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            email TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            age TEXT,
            gender TEXT,
            address TEXT,
            profile_pic TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def save_user(uid, email, name, phone="", age="", gender="", address="", profile_pic=""):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO users (uid, email, name, phone, age, gender, address, profile_pic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (uid, email, name, phone, age, gender, address, profile_pic))
    conn.commit()
    conn.close()
    
def get_user_by_email(email):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user