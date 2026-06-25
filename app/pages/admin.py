import streamlit as st
import sqlite3
import pandas as pd

st.title("Administração")

conn = sqlite3.connect("data/city_noise.db")

df = pd.read_sql(
    "SELECT * FROM noise_reports ORDER BY id DESC",
    conn
)

conn.close()

st.dataframe(df, use_container_width=True)