import os
import random
import osmnx as ox
import geopandas as gpd
import pandas as pd
import folium


# # ============================================================
# # 1. BAIXAR MALHA VIÁRIA DE BELÉM
# # ============================================================
print("Baixando ruas de Belém...")
G = ox.graph_from_place("Belém, Pará, Brazil", network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
edges = edges.reset_index()
# # ============================================================
# # 2. FUNÇÃO: GERAR PONTO ALEATÓRIO EM UMA RUA
# # ============================================================
def gerar_ponto_aleatorio_em_rua(geom):
    distancia_random = random.uniform(0, geom.length)
    return geom.interpolate(distancia_random)


# ============================================================
# 3. CARREGAR SHAPE DOS BAIRROS
# ============================================================
path = "/home/akel/PycharmProjects/city_noise/data/raw/"
arquivo = os.path.join(path, "shape_bairros.gpkg")

gdf_bairros = gpd.read_file(arquivo).rename(columns={'NM_BAIRRO': 'Bairro'})
bairros4674 = gdf_bairros.to_crs("EPSG:4674")
edges = edges.to_crs("EPSG:4674")

# ============================================================
# 4. CARREGAR TABELA DE DESCARTES IRREGULARES ML
# ============================================================
df_temp = pd.read_csv(os.path.join(path, "Bairros_features.csv"))
df_registro = (
    df_temp[['Bairro', 'Registros']])

lista_bairros = df_registro['Bairro'].tolist()

# ============================================================
# 5. GERAR PONTOS ALEATÓRIOS POR BAIRRO
# ============================================================
pontos = []
ponto_bairro = []   # <- necessário para colorir depois

for bairro in lista_bairros:
    # Número de descartes no bairro
    N = int(df_registro.loc[df_registro["Bairro"] == bairro, "Registros"].iloc[0])

    # Seleciona o polígono do bairro
    bairro_geom = bairros4674[bairros4674["Bairro"] == bairro]

    # Interseção com ruas
    ruas_no_bairro = gpd.overlay(edges, bairro_geom, how="intersection")

    if ruas_no_bairro.empty:
        #print(f"⚠️ Sem ruas no bairro: {bairro}")
        continue

    # Gera N pontos aleatórios
    for _ in range(N):
        rua_escolhida = ruas_no_bairro.sample(1).iloc[0]
        ponto = gerar_ponto_aleatorio_em_rua(rua_escolhida.geometry)
        pontos.append(ponto)
        ponto_bairro.append(bairro)   # ← registrando o bairro do ponto

# ============================================================
# 6. CRIAR GEODataFrame DOS PONTOS
# ============================================================
gdf_pontos = gpd.GeoDataFrame(geometry=pontos, crs="EPSG:4326")
gdf_pontos["lat"] = gdf_pontos.geometry.y
gdf_pontos["lon"] = gdf_pontos.geometry.x

# ============================================================
# 7. CRIAR MAPA COM PONTOS
# ============================================================
centro = [gdf_pontos["lat"].mean(), gdf_pontos["lon"].mean()]
mapa = folium.Map(location=centro, zoom_start=12)

for _, row in gdf_pontos.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=4,
        color="red",
        fill=True,
        fill_color="red",
    ).add_to(mapa)

import webbrowser

# Salva o mapa como um arquivo HTML na pasta do seu projeto
mapa.save("mapa_belem.html")

# Abre o arquivo automaticamente no seu navegador padrão
webbrowser.open("mapa_belem.html")