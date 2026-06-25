#db.py
import sqlite3
from datetime import datetime
import os

DB_PATH = "data/city_noise.db"


def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS noise_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        latitude REAL,
        longitude REAL,
        address TEXT,
        origem TEXT,
        frequencia TEXT,
        periodo TEXT,
        duracao REAL,
        incomodo TEXT,
        db_level REAL,
        observacoes TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_report(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO noise_reports (
        timestamp, latitude, longitude, address,
        origem, frequencia, periodo, duracao,
        incomodo, db_level, observacoes
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        data["lat"],
        data["lon"],
        data["address"],
        data["origem"],
        data["frequencia"],
        data["periodo"],
        data["duracao"],
        data["incomodo"],
        data["db"],
        data["observacoes"]
    ))

    conn.commit()
    conn.close()