#app_0.1.py  vs0.15
import streamlit as st
import folium
import json

from streamlit_folium import st_folium

from setup import setup_path
setup_path()

from src.geo.geocoder_photon import geocode_address, reverse_geocode
#from src.input.db import init_db, save_report
from src.input.db import init_db
from src.input.repository import save_report



# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="city noise", layout="centered")
init_db()


#st.image("app/capa3.png", use_container_width=True) #streamlit
# st.image("capa3.png", use_container_width=True) #local
#
# st.title("CITY - NOISES  0.15" )

# ----------------------------
# CONFIGURAÇÃO DA CAPA COM IMAGEM LOCAL + BASE64
# ----------------------------
import base64
# 1. Encontra o caminho absoluto da imagem (ajustado para o mesmo diretório do script)
caminho_da_imagem = "app/capa3.png" #streamlit

# 2. Função para transformar a imagem em formato que o HTML entenda
def obter_imagem_base64(caminho):
    with open(caminho, "rb") as arquivo_imagem:
        dados_da_imagem = arquivo_imagem.read()
    return base64.b64encode(dados_da_imagem).decode()

try:
    # 3. Codifica a imagem
    imagem_base64 = obter_imagem_base64(caminho_da_imagem)
    imagem_url = f"data:image/png;base64,{imagem_base64}"
except FileNotFoundError:
    # Fallback caso a imagem suma por algum motivo
    imagem_url = ""

# 4. Renderiza o HTML com o título sobreposto
st.markdown(
    f"""
    <div style="
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('{imagem_url}');
        background-color: #262730; /* Cor de fundo caso a imagem falhe */
        background-size: cover;
        background-position: center;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 12px;
        color: white;
        text-align: center;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h1 style="
            margin: 0; 
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
            font-size: 2rem; 
            font-weight: 800; 
            letter-spacing: 2px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
        ">
            CITY - NOISES 0.15
        </h1>
        <p style="
            margin: 10px 0 0 0; 
            font-size: 1.2rem; 
            font-weight: 300;
            opacity: 0.9;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
        ">
            Mapeamento de poluição sonora
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
# ----------------------------
# FIM CONFIGURAÇÃO DA CAPA
# ----------------------------

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

if "sucesso_registro" not in st.session_state:
    st.session_state.sucesso_registro = False



# ----------------------------
# ETAPA 1 - LOCALIZAÇÃO
# ----------------------------


if st.session_state.step == "location":

    # if "sucesso_registro" in st.session_state and st.session_state.sucesso_registro:
    #     st.success(st.session_state.sucesso_registro)
    #     # Deleta ou limpa para sumir na próxima interação com o mapa
    #     del st.session_state.sucesso_registro


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
        ["Hoje","Todos os dias","seg-sex","Finais de semana", "Ocasionalmente"]
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

        #st.success("Ocorrência registrada com sucesso!")
        #st.session_state.sucesso_registro = "Ocorrência registrada com sucesso!"
        st.session_state.sucesso_registro = True

        # reset
        st.session_state.location = None
        st.session_state.address = None
        st.session_state.map_center = [-1.4558, -48.4902]
        st.session_state.step = "location"

        st.rerun()

# ----------------------------
# TELA INTERMEDIÁRIA DE SUCESSO
# ----------------------------
if st.session_state.sucesso_registro:
    st.success("🎉 Ocorrência registrada com sucesso!")
    st.write("Obrigado por colaborar com o mapeamento de ruídos da cidade.")

    #st.divider()

    # O botão que o usuário clica quando decide fazer um novo registro
    if st.button("🔄 Fazer novo registro", use_container_width=True):
        # Reseta COMPLETAMENTE o estado para o início
        st.session_state.location = None
        st.session_state.address = None
        st.session_state.map_center = [-1.4558, -48.4902]
        st.session_state.step = "location"
        st.session_state.sucesso_registro = False  # Desativa a tela de sucesso

        st.rerun()

    # Interrompe a execução do resto do script para não mostrar o formulário ou o mapa atrás
    st.stop()


