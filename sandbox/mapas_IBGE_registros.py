#!/usr/bin/env python
# coding: utf-8

# ## Filtragem base da dados
# * leitura dos dados
# * Filtragem 
# * Seleção das colunas relevantes
#   

# In[1]:


import pandas as pd
import folium
from setup_notebook import setup_path
setup_path()
from src.utils.functions import *
from folium.plugins import FastMarkerCluster
import webbrowser
import os
import time


# In[2]:


#leitura do arquivo
arquivo_csv = '/home/akel/PycharmProjects/city_noise/data/raw/1501402_BELEM.csv'

# 2. Ler o arquivo CSV
df = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8', low_memory=False)
inital_describe(df,True)


# In[3]:


# Filtragem
# Garante que as colunas estão em maiúsculo e sem NaNs para o filtro funcionar
df['DSC_ESTABELECIMENTO'] = df['DSC_ESTABELECIMENTO'].astype(str).str.upper()

# REGEX
# 1. BAR\Boteco isolados
padrao_bar = r'\bBAR\b|\bBOTECO\b'

# 2. DEPOSITO DE BEBIDAS: Captura "DEPOSITO DE BEBIDAS", "DEPOSITO DE CERVEJA" ou apenas "DEPOSITO" puro
padrao_deposito = r'DEPOSITO.*BEBIDA|DEPOSITO.*CERVEJA'

# 3. Outros padrões
padrao_outros = r'CHURRASC|RESTAURANTE|CASA DE SHOW|CASA DE EVENTOS|RECEPÇÕE|CAFE'
padrao_sinuca = r'\bSINUCA\b|\bBILHAR\b'

# Agregando Padrões de Busca
procura_geral = f"{padrao_bar}|{padrao_deposito}|{padrao_sinuca}|{padrao_outros}"


# 4. Exclusões explícitas para limpar o "DEPOSITO" genérico de falsos positivos
padrao_exclusao = r'GAS|AGUA|RECICLA|CONSTRUCA|MATERIAL|MOVEIS|FERRO|CIMENTO|' \
                  r'MERCADORIAS|MADEIRA|MATERIAIS|FARINHA|FERRAGENS|MAQUINAS|' \
                  r'CALCADOS|VAGO|TINTAS|MARISCOS'


# FILTROS
# filtro 1: Padrão de busca

df_filt = df[df['DSC_ESTABELECIMENTO'].str.contains(procura_geral, na=False, regex=True)]

# filtro 2: remove termos dentro dos padrões encontrados

df_filt = df_filt[~df_filt['DSC_ESTABELECIMENTO'].str.contains(padrao_exclusao, na=False, regex=True)]

#resetando index
df_filt = df_filt.reset_index(drop=True)

print("\nAmostra dos estabelecimentos encontrados:")
print(df_filt['DSC_ESTABELECIMENTO'].value_counts().head(40))
inital_describe(df_filt,True)


# In[4]:


# 5. Criar o mapa centralizado na média dos pontos filtrados
centro_lat = df_filt['LATITUDE'].dropna().mean()
centro_lon = df_filt['LONGITUDE'].dropna().mean()
centro = [centro_lat, centro_lon]

mapa = folium.Map(location=centro, zoom_start=12)

# 6. Adicionar os marcadores utilizando o DataFrame filtrado correto
for _, row in df_filt.dropna(subset=['LATITUDE', 'LONGITUDE']).iterrows():
    folium.CircleMarker(
        location=[row["LATITUDE"], row["LONGITUDE"]],
        radius=4,
        color="red",
        fill=True,
        fill_color="red",
        # Opcional: adiciona o nome do estabelecimento como popup ao clicar
        popup=row["DSC_ESTABELECIMENTO"] 
    ).add_to(mapa)

# Mostrar mapa
mapa


# In[5]:


df_filt.columns


# In[6]:


# juntar 3 colunas para formar o endereco_comleto
df_filt['END_COMPLETO'] = (df_filt['NOM_TIPO_SEGLOGR'].fillna('') + ' '+df_filt['NOM_TITULO_SEGLOGR'].fillna('') + ' ' + df_filt['NOM_SEGLOGR'].fillna('')).str.strip()

#df_filt[['COD_DISTRITO','CEP','DSC_LOCALIDADE', 'NOME_COMPLETO','NUM_ENDERECO','LATITUDE', 'LONGITUDE','DSC_ESTABELECIMENTO', 'COD_INDICADOR_ESTAB_ENDERECO']].head(50)

#salvar arquivo

df_export = df_filt[['COD_DISTRITO','CEP','DSC_LOCALIDADE', 'END_COMPLETO','NUM_ENDERECO','LATITUDE', 'LONGITUDE','DSC_ESTABELECIMENTO', 'COD_INDICADOR_ESTAB_ENDERECO']]
df_export.to_csv('/home/akel/PycharmProjects/city_noise/data/processed/Bares_etc_Belem_filt.csv', index=False, encoding='utf-8-sig')
print(f"Arquivo salvo com {len(df_export)} registros!")
print("\n#Arquivos salvos", time.strftime("%H:%M:%S"))

