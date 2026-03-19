import sqlite3

DB_NAME = "ballroom.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # MEMBERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
    """)

    # LESSONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_date TEXT,
        time TEXT,
        type TEXT
    )
    """)

    # SIGNUPS (form responses)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS signups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        lesson_id INTEGER,
        is_driver TEXT,
        seats INTEGER,
        FOREIGN KEY(member_id) REFERENCES members(id),
        FOREIGN KEY(lesson_id) REFERENCES lessons(id)
    )
    """)

    # ATTENDANCE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        lesson_id INTEGER,
        timestamp TEXT,
        FOREIGN KEY(member_id) REFERENCES members(id),
        FOREIGN KEY(lesson_id) REFERENCES lessons(id)
    )
    """)

    # CREDITS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS credits (
        member_id INTEGER PRIMARY KEY,
        total_credits INTEGER,
        remaining_credits INTEGER,
        FOREIGN KEY(member_id) REFERENCES members(id)
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()