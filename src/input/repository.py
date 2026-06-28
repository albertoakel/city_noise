#repository.py
from src.input.db import save_report as save_sqlite

from src.input.sheets import save_google
from datetime import datetime


def save_report(data):

    data["timestamp"] = datetime.now().isoformat()

    save_sqlite(data)

    save_google(data)