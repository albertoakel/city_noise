#sheets.py
import gspread
import pandas as pd
import streamlit as st

from oauth2client.service_account import (
    ServiceAccountCredentials
)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def connect_sheet():

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scope
    )

    client = gspread.authorize(creds)

    sheet = client.open(
        st.secrets["SHEET_NAME"]
    ).sheet1

    return sheet


def save_google(data):

    sheet = connect_sheet()

    sheet.append_row([

        data["timestamp"],
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

    ])


def load_google():

    sheet = connect_sheet()

    registros = sheet.get_all_records()

    return pd.DataFrame(registros)



