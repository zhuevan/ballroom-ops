import pandas as pd
import sqlite3
import re
import gspread
from google.oauth2.service_account import Credentials

def fetch_sheet_data():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1vWPrFQoOKXfaIihTPAFmJyk0isuUj75jNk4Y30hny60/edit?gid=984507337#gid=984507337"
    ).sheet1

    return sheet.get_all_records()

DB_NAME = "ballroom.db"

LESSON_DATES = [
    "2025-01-27",
    "2025-02-03",
    "2025-02-17",
    "2025-02-24",
    "2025-03-03",
    "2025-03-17",
    "2025-03-24",
    "2025-03-31",
    "2025-04-07",
    "2025-04-14",
    "2025-04-21",
    "2025-04-28",
    "2026-01-27",
    "2026-02-03",
    "2026-02-17",
    "2026-02-24",
    "2026-03-03",
    "2026-03-17",
    "2026-03-24",
    "2026-03-31",
    "2026-04-07",
    "2026-04-14",
    "2026-04-21",
    "2026-04-28",
]


# -------------------------
# Helpers
# -------------------------

def normalize_email(email):
    return email.strip().lower()


def parse_driver(driver_text):
    if pd.isna(driver_text):
        return "rider"

    driver_text = driver_text.lower()

    if "yes" in driver_text:
        return "driver"
    if "no" in driver_text:
        return "self"

    return "rider"


def parse_seats(seat_text, is_driver):
    if pd.isna(seat_text):
        return 4 if is_driver else 0  # default assumption

    # extract first number from string
    match = re.search(r"\d+", str(seat_text))
    if match:
        return int(match.group())
    return 4 if is_driver else 0


def parse_lessons(lesson_text):
    if pd.isna(lesson_text):
        return []

    lesson_text = str(lesson_text)

    # Split by comma
    raw_lessons = lesson_text.split(",")

    cleaned = []
    for l in raw_lessons:
        l = l.strip()

        # Only keep things that look like lessons
        if "-" in l and "pm" in l:
            cleaned.append(l)

    return cleaned

def parse_lesson(lesson_str):
    lesson_str = lesson_str.strip()

    # Normalize formatting
    lesson_str = lesson_str.replace("-", " - ")

    parts = [p.strip() for p in lesson_str.split(" - ") if p.strip()]

    if len(parts) < 2:
        print(f"SKIPPING BAD LESSON: '{lesson_str}'")
        return None, None

    time = parts[0]
    lesson_type = parts[1]

    return time, lesson_type
def parse_timestamp_to_event_date(timestamp):
    signup_dt = pd.to_datetime(timestamp)

    for event_date_str in LESSON_DATES:
        cutoff_dt = pd.Timestamp(f"{event_date_str} 12:00:00")
        if signup_dt < cutoff_dt:
            return event_date_str

    return None


# -------------------------
# DB helpers
# -------------------------

def get_or_create_member(cur, name, email):
    email = normalize_email(email)

    cur.execute("SELECT id FROM members WHERE email = ?", (email,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        "INSERT INTO members (name, email) VALUES (?, ?)",
        (name.strip(), email)
    )
    return cur.lastrowid


def get_or_create_lesson(cur, event_date, time, lesson_type):
    cur.execute("""
    SELECT id FROM lessons
    WHERE event_date = ? AND time = ? AND type = ?
    """, (event_date, time, lesson_type))

    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute("""
    INSERT INTO lessons (event_date, time, type)
    VALUES (?, ?, ?)
    """, (event_date, time, lesson_type))

    return cur.lastrowid


# -------------------------
# Main ingestion
# -------------------------

def ingest_csv(file_path):
    rows = fetch_sheet_data()
    df = pd.DataFrame(rows)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for _, row in df.iterrows():

        name = row["Name"]
        email = row["Email"]

        lessons = parse_lessons(row["Which lessons?"])
        is_driver = parse_driver(row["Are you willing to drive people in your car for the carpool? "])
        seats = parse_seats(row["If you said you can drive, how many passengers can you take?"], is_driver)

        member_id = get_or_create_member(cur, name, email)

        event_date = parse_timestamp_to_event_date(row["Timestamp"])
       
        if event_date is None:
            print(f"SKIPPING ROW AFTER LAST EVENT DATE: {row['Timestamp']} | {row['Name']}")
            continue

        for lesson in lessons:
            time, lesson_type = parse_lesson(lesson)
            if time is None:
                continue

            lesson_id = get_or_create_lesson(
                cur,
                event_date,
                time,
                lesson_type
            )

            cur.execute("""
            INSERT INTO signups (member_id, lesson_id, is_driver, seats)
            VALUES (?, ?, ?, ?)
            """, (member_id, lesson_id, is_driver, seats))

    conn.commit()
    conn.close()


# -------------------------
# Run
# -------------------------

if __name__ == "__main__":
    ingest_csv("data/raw/forms.csv")