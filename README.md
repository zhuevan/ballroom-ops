Ballroom Lesson Operations System

Backend system to manage lesson sign-ups, carpool logistics, and attendance for a university ballroom dance team, replacing manual spreadsheet workflows.

Features
Sign-ups: Track member registrations across lesson levels
Carpool: Match riders to drivers based on availability and seat capacity
Ingestion: Parse and clean Google Form data
Attendance: Structured tracking (extensible for QR check-in)
Tech Stack

Python, SQLite, FastAPI, SQLModel

Structure
app/
  main.py        # API entry
  db.py          # DB setup
  models.py      # Data models
  carpool.py     # Matching logic
  ingest.py      # Data ingestion
data/raw/        # Input CSVs
schema.sql
Usage
python app/ingest.py
python app/carpool.py
uvicorn app.main:app --reload
Impact

Centralizes operations, reduces manual coordination, and scales to 50+ members.
