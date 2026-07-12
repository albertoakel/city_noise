import json
import time
import pandas as pd
import requests


def coletar_estabelecimentos_belem():
    # Alterado para HTTPS
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Query OverpassQL
    overpass_query = """
        [out:json][timeout:180];
        area["name"="Belém"]["boundary"="administrative"] -> .searchArea;
        (
          node["amenity"="restaurant"](area.searchArea);
          way["amenity"="restaurant"](area.searchArea);

          node["amenity"="bar"](area.searchArea);
          way["amenity"="bar"](area.searchArea);

          node["amenity"="pub"](area.searchArea);
          way["amenity"="pub"](area.searchArea);

          node["shop"="alcohol"](area.searchArea);
          way["shop"="alcohol"](area.searchArea);

          node["amenity"="nightclub"](area.searchArea);
          way["amenity"="nightclub"](area.searchArea);
        );
        out center;
        """

    # CRUCIAL: Definir um User-Agent para evitar o erro 406
    headers = {
        "User-Agent": "MapeamentoBelemBot/1.0 (meu_email_ou_projeto@email.com)",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    print("Enviando requisição para a Overpass API (OpenStreetMap)...")

    try:
        # Enviamos a query diretamente no parâmetro 'data' com os headers configurados
        response = requests.post(
            overpass_url, data={"data": overpass_query}, headers=headers, timeout=120
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com a API: {e}")
        if response is not None:
            print(f"Detalhes do erro do servidor: {response.text}")
        return None

    elementos = data.get("elements", [])
    print(f"Total de registros encontrados: {len(elementos)}")

    lista_locais = []

    for elem in elementos:
        tags = elem.get("tags", {})

        lat = elem.get("lat") or elem.get("center", {}).get("lat")
        lon = elem.get("lon") or elem.get("center", {}).get("lon")

        rua = tags.get("addr:street", "")
        numero = tags.get("addr:housenumber", "")
        bairro = tags.get("addr:suburb", "")

        if rua:
            endereco_completo = f"{rua}, {numero}".strip(", ")
            if bairro:
                endereco_completo += f" - {bairro}"
        else:
            endereco_completo = (
                "Endereço não disponível no OSM (Apenas Coordenadas)"
            )

        info = {
            "id": elem.get("id"),
            "nome": tags.get("name", "Sem Nome Registrado"),
            "categoria": tags.get("amenity"),
            "endereco_rua": rua,
            "numero": numero,
            "bairro": bairro,
            "endereco_formatado": endereco_completo,
            "latitude": lat,
            "longitude": lon,
            "cuisine": tags.get("cuisine", "Não especificada"),
            "site": tags.get("website", ""),
        }
        lista_locais.append(info)

    if not lista_locais:
        return pd.DataFrame()

    df = pd.DataFrame(lista_locais)

    traducao_categorias = {
        "restaurant": "Restaurante",
        "bar": "Bar",
        "pub": "Pub/Bar",
        "nightclub": "Casa de Show/Boate",
        "alcohol": "depósito",

    }
    df["categoria"] = df["categoria"].map(traducao_categorias)

    return df


if __name__ == "__main__":
    df_locais = coletar_estabelecimentos_belem()

    if df_locais is not None and not df_locais.empty:
        csv_filename = "estabelecimentos_belem.csv"
        df_locais.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        print(f"Dados salvos com sucesso em: {csv_filename}")

        print("\nResumo por Categoria:")
        print(df_locais["categoria"].value_counts())

        print("\nExemplo dos primeiros dados coletados:")
        print(df_locais[["nome", "categoria", "bairro"]].head())
    else:
        print("Nenhum dado foi gerado ou a base retornou vazia.")