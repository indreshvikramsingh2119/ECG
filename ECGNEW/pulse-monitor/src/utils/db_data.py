def init_db():
    # Initialize the database connection and create necessary tables
    import sqlite3

    conn = sqlite3.connect('pulse_monitor.db')
    cursor = conn.cursor()

    # Create a users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def save_user(user_id, email, name):
    # Save user information to the database
    import sqlite3

    conn = sqlite3.connect('pulse_monitor.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO users (id, email, name, password)
        VALUES (?, ?, ?, ?)
    ''', (user_id, email, name, ''))  # Password should be handled securely

    conn.commit()
    conn.close()