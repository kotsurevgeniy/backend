import sqlite3

def init_db():
    with sqlite3.connect("trainings.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trainings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                time TEXT,
                distance REAL,
                avg_speed REAL,
                avg_pulse INTEGER,
                track_link TEXT,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)