import geopandas as gpd

#atualiza/corrige nome dos bairros dada uma posição geografica


# atualiza/corrige nome dos bairros dada uma posição geografica
def atualizar_bairros(df, coluna_bairro="Bairros",
                      coluna_lat="LATITUDE",
                      coluna_lon="LONGITUDE",
                      crs_projetado="EPSG:31982"): # <- ver melhor datum para a cidade. https://epsg.io/map#srs=31982&x=802805.176729&y=9891127.048129&z=5&reproject=1&layer=osm

    path = "/home/akel/PycharmProjects/city_noise/data/raw/"
    gdf_bairros = (gpd.read_file(path + "shape_bairros.gpkg")
           .rename(columns={"NM_BAIRRO": "Bairro"})
           )

    gdf_bairros['Bairro'] = (
        gdf_bairros['Bairro']
        .astype(str)
        .str.upper()
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.strip()
    )

    df = df.copy()

    # Seleciona apenas bairros indefinidos
    mask = df[coluna_bairro] == "INDEFINIDO"

    if mask.sum() == 0:
        print("Nenhum bairro INDEFINIDO encontrado.")
        return df

    # Cria GeoDataFrame dos pontos (inicialmente em graus)
    gdf_pontos = gpd.GeoDataFrame(
        df.loc[mask].copy(),
        geometry=gpd.points_from_xy(
            df.loc[mask, coluna_lon],
            df.loc[mask, coluna_lat]
        ),
        crs="EPSG:4326"
    )

    # Garante mesmo CRS para o primeiro join funcional (dentro do polígono)
    gdf_bairros = gdf_bairros.to_crs(gdf_pontos.crs)

    # Spatial Join padrão (pontos estritamente DENTRO do bairro)
    resultado = gpd.sjoin(
        gdf_pontos,
        gdf_bairros[["Bairro", "geometry"]],
        how="left",
        predicate="within"
    )

    # Procura o bairro mais próximo para pontos fora dos polígonos
    faltantes = resultado["Bairro"].isna()

    if faltantes.any():
        # --- CORREÇÃO DO AVISO ---
        # Reprojetamos apenas os pontos faltantes e o mapa de bairros para metros
        pontos_faltantes_proj = resultado[faltantes].drop(columns=["index_right", "Bairro"], errors="ignore").to_crs(crs_projetado)
        gdf_bairros_proj = gdf_bairros[["Bairro", "geometry"]].to_crs(crs_projetado)

        prox = gpd.sjoin_nearest(
            pontos_faltantes_proj,
            gdf_bairros_proj,
            how="left",
            distance_col="distancia" # Agora a distância estará salva em metros!
        )

        # O índice original se mantém na reprojeção, então o mapeamento continua correto
        resultado.loc[prox.index, "Bairro"] = prox["Bairro"]

    # Atualiza o DataFrame original
    df.loc[resultado.index, coluna_bairro] = resultado["Bairro"].values

    print(f"{mask.sum()} bairros indefinidos processados.")
    print(f"{resultado['Bairro'].notna().sum()} bairros atualizados.")
    print(f"{resultado['Bairro'].isna().sum()} permaneceram sem bairro.")

    return df