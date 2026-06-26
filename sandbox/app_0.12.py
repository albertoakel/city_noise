#app_0.12.py
import streamlit as st
import folium
import json

from streamlit_folium import st_folium

from setup import setup_path
setup_path()

from src.geo.geocoder import geocode_address, reverse_geocode
from src.input.db import init_db, save_report

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="city noise", layout="centered")
init_db()

st.title("C I T Y   N O I S E S")

# ----------------------------
# ESTADO
# ----------------------------
if "location" not in st.session_state:
    st.session_state.location = None

if "address" not in st.session_state:
    st.session_state.address = None

# ----------------------------
# ETAPA 1 - LOCALIZAÇÃO
# ----------------------------
st.header("1. Localização")
st.caption("Informe onde o ruído ocorre.")

option = st.radio(
    "Como deseja informar a localização?",
    ["Digite o endereço", "Selecionar no mapa"]
)

# ---- ENDEREÇO ----
if option == "Digite o endereço":
    address_input = st.text_input("Digite o endereço (ex: Av. Almirante Barroso, 2500, Belém)")

    if st.button("Buscar endereço"):
        result = geocode_address(address_input)

        if result:
            st.session_state.location = (result["lat"], result["lon"])
            st.session_state.address = result["address"]
            st.success(result["address"])
        else:
            st.error("Endereço não encontrado.")

# ---- MAPA ----
else:
    m = folium.Map(location=[-1.4558, -48.4902], tiles="OpenStreetMap",
        zoom_start=14)

    map_data = st_folium(m, height=300, width=None)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        st.session_state.location = (lat, lon)

        addr = reverse_geocode(lat, lon)
        st.session_state.address = addr

        #st.success(addr)

# ----------------------------
# CONFIRMAÇÃO
# ----------------------------
if st.session_state.location and st.session_state.address:
    st.subheader("📌 Confirmar localização")

    st.info(st.session_state.address)

    if st.button("Confirmar e continuar"):
        st.session_state.step = "form"

# ----------------------------
# ETAPA 2 - FORMULÁRIO
# ----------------------------
if st.session_state.get("step") == "form":

    st.header("2. Dados da ocorrência")

    origem = st.selectbox(
        "Origem do barulho",
        [
            "Som de carro (propaganda)",
            "Autofalantes em residências",
            "Festa em bares",
            "Paredão, Trio e Aparelhagens",
            "Trânsito intenso",
            "Obras/Construção",
            "Eventos públicos",
            "Outros"
        ]
    )

    frequencia = st.selectbox(
        "Frequência",
        ["Todos os dias","seg-sex","Finais de semana", "Ocasionalmente"]
    )

    periodo = st.multiselect(
        "Período",
        ["Manhã", "Tarde", "Noite", "Madrugada"]
    )



    duracao = st.slider("Duração (horas)", 0.0, 15.0, 1.0)

    incomodo = st.selectbox(
        "Nível de incômodo",
        ["Baixo", "Médio", "Alto"]
    )

    db = st.slider("Estimativa de dB", 0, 150, 60)

    observacoes =  st.text_area(
    "Observações",
    height=120
)

    # ----------------------------
    # SALVAR
    # ----------------------------
    if st.button("📩 Registrar ocorrência",use_container_width=True):

        lat, lon = st.session_state.location

        data = {
            "lat": lat,
            "lon": lon,
            "address": st.session_state.address,
            "origem": origem,
            "frequencia": frequencia,
            "periodo": json.dumps(periodo),
            "duracao": duracao,
            "incomodo": incomodo,
            "db": db,
            "observacoes": observacoes
        }

        save_report(data)

        st.success("Ocorrência registrada com sucesso!")

        # reset
        st.session_state.location = None
        st.session_state.address = None
        st.session_state.step = None