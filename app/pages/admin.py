#admin.py
import streamlit as st
import sqlite3
import pandas as pd

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

if not st.session_state.admin_logado:

    senha = st.text_input(
        "Senha de administrador",
        type="password"
    )

    if st.button("Entrar"):

        if senha == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.admin_logado = True
            st.rerun()

        else:
            st.error("Senha incorreta")

    st.stop()

st.title("Administração")

conn = sqlite3.connect("data/city_noise.db")

df = pd.read_sql(
    "SELECT * FROM noise_reports ORDER BY id DESC",
    conn
)

conn.close()

st.dataframe(df, use_container_width=True)