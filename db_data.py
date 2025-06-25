import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (uid TEXT PRIMARY KEY, email TEXT, name TEXT)''')
    conn.commit()
    conn.close()

def save_user(uid, email, name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (uid, email, name) VALUES (?, ?, ?)', (uid, email, name))
    conn.commit()
    conn.close()