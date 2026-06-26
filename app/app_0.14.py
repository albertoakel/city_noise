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

st.title("CITY - NOISES  0.14" )

# ----------------------------
# ESTADO
# ----------------------------
if "location" not in st.session_state:
    st.session_state.location = None

if "address" not in st.session_state:
    st.session_state.address = None

# ----------------------------
# ESTADO
# ----------------------------

if "location" not in st.session_state:
    st.session_state.location = None

if "address" not in st.session_state:
    st.session_state.address = None

if "map_center" not in st.session_state:
    st.session_state.map_center = [-1.4558, -48.4902]  # Belém

if "address" not in st.session_state:
    st.session_state.address = None

if "step" not in st.session_state:
    st.session_state.step = "location"

# ----------------------------
# ETAPA 1 - LOCALIZAÇÃO
# ----------------------------


if st.session_state.step == "location":

    st.header("1. Localização")
    st.caption("Informe onde o ruído ocorre.")

    address_input = st.text_input(
        "Digite um endereço (opcional)"
    )

    if st.button("🔍 Buscar endereço", use_container_width=True):
        with st.spinner("Localizando endereço..."):
            result = geocode_address(address_input)

        if result:

            st.session_state.location = (
                result["lat"],
                result["lon"]
            )

            st.session_state.address = result["address"]

            st.session_state.map_center = [
                result["lat"],
                result["lon"]
            ]

            st.session_state.step = "confirm"

            st.rerun()

        else:
            st.error("❌ Endereço não encontrado.")

    # ----------------------------
    # MAPA
    # ----------------------------

    m = folium.Map(
        location=st.session_state.map_center,
        tiles="OpenStreetMap",
        zoom_start=16
    )

    if st.session_state.location:

        lat, lon = st.session_state.location

        folium.Marker(
            [lat, lon],
            tooltip="Localização selecionada",
            icon=folium.Icon(color="red")
        ).add_to(m)

    map_data = st_folium(
        m,
        height=300,
        width=None
    )

    if map_data and map_data.get("last_clicked"):

        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        st.session_state.location = (lat, lon)
        st.session_state.map_center = [lat, lon]

        with st.spinner("Obtendo endereço..."):
            st.session_state.address = reverse_geocode(lat, lon)

        st.session_state.step = "confirm"

        st.rerun()
# ----------------------------
# ETAPA 2 - CONFIRMAÇÃO
# ----------------------------

if st.session_state.step == "confirm":

    st.header("2. Confirmar localização")

    st.success(st.session_state.address)

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Continuar",
            use_container_width=True
        ):
            st.session_state.step = "form"
            st.rerun()

    with col2:

        if st.button(
            "Alterar localização",
            use_container_width=True
        ):
            st.session_state.step = "location"
            st.rerun()
# ----------------------------
# ETAPA 2 - FORMULÁRIO
# ----------------------------
if st.session_state.get("step") == "form":

    st.header("2. Dados da ocorrência")
    st.info(f"{st.session_state.address}")

    if st.button("⬅ Alterar localização"):
        st.session_state.step = "location"
        st.rerun()

    st.divider()

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
        st.session_state.map_center = [-1.4558, -48.4902]
        st.session_state.step = "location"

        st.rerun()