import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
import webbrowser
import os

# 1. Definir o nome do arquivo de origem
arquivo_csv = '1501402_BELEM.csv'

print("Carregando os dados...")
# 2. Ler o arquivo CSV
df = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8', low_memory=False)

print("Filtrando e limpando os dados...")
# 3. FILTRO: Converter para numérico e filtrar apenas FINALIDADE igual a 2 ou 3
df['COD_INDICADOR_FINALIDADE_CONST'] = pd.to_numeric(df['COD_INDICADOR_FINALIDADE_CONST'], errors='coerce')
df_filtrado = df[df['COD_INDICADOR_FINALIDADE_CONST'].isin([2, 3,4])]

# Remover linhas que não tenham LATITUDE ou LONGITUDE válidas dentro do grupo filtrado
df_coords = df_filtrado[['LATITUDE', 'LONGITUDE']].dropna()

# Garantir que as coordenadas estejam no formato float
df_coords['LATITUDE'] = df_coords['LATITUDE'].astype(float)
df_coords['LONGITUDE'] = df_coords['LONGITUDE'].astype(float)

print(f"Total de registros encontrados com finalidade 2 ou 3: {len(df_coords)}")

# Se nenhum registro passar pelo filtro, interrompe para evitar erro no mapa
if len(df_coords) == 0:
    print("Aviso: Nenhum registro encontrado com os critérios informados. Verifique o arquivo.")
else:
    # 4. Criar o mapa base
    print("Gerando o mapa base...")
    centro_lat = df_coords['LATITUDE'].mean()
    centro_lon = df_coords['LONGITUDE'].mean()

    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=12)

    # 5. Adicionar os pontos agrupados filtrados
    print("Adicionando os marcadores ao mapa...")
    coordenadas = df_coords[['LATITUDE', 'LONGITUDE']].values.tolist()
    FastMarkerCluster(data=coordenadas).add_to(mapa)

    # 6. Salvar o mapa gerado em um arquivo HTML
    nome_mapa_html = "mapa_estabelecimentos_belem.html"
    mapa.save(nome_mapa_html)

    # 7. Abrir no navegador
    caminho_absoluto = 'file://' + os.path.realpath(nome_mapa_html)
    webbrowser.open(caminho_absoluto)

    print(f"\nMapa gerado com sucesso!")
    print(f"Para visualizar, basta abrir o arquivo '{nome_mapa_html}' no seu navegador web.")