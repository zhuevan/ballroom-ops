from fastapi import FastAPI
from app.db import get_db
from app.services.carpool import generate_carpools_for_date
from datetime import datetime
from pydantic import BaseModel

class AttendanceRequest(BaseModel):
    member_id: int
    lesson_id: int

app = FastAPI()


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/members")
def get_members():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM members")
    rows = cur.fetchall()

    return [dict(row) for row in rows]


@app.get("/carpools/{event_date}")
def carpools(event_date: str):
    return generate_carpools_for_date(event_date)


@app.post("/attendance")
def mark_attendance(data: AttendanceRequest):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO attendance (member_id, lesson_id, timestamp)
    VALUES (?, ?, ?)
    """, (data.member_id, data.lesson_id, datetime.now().isoformat()))

    conn.commit()

    return {"status": "recorded"}