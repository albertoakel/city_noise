import json
import time
import pandas as pd
import requests


def coletar_estabelecimentos_belem():
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Query OverpassQL
    # CORREÇÃO 1: adicionado shop=convenience (lojas de conveniência)
    # e shop=beverages (depósitos de bebida no padrão "liquor_store" do
    # Google Maps), ambos ausentes da query original.
    # AMPLIAÇÃO: incluídas mais categorias com potencial de aglomeração
    # noturna e geração de barulho (cafés que viram bar à noite,
    # biergarten, casas de jogos, casas noturnas, salões de dança/forró,
    # espaços de eventos, lojas de vinho etc.)
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

          node["amenity"="cafe"](area.searchArea);
          way["amenity"="cafe"](area.searchArea);

          node["amenity"="biergarten"](area.searchArea);
          way["amenity"="biergarten"](area.searchArea);

          node["amenity"="nightclub"](area.searchArea);
          way["amenity"="nightclub"](area.searchArea);

          node["amenity"="casino"](area.searchArea);
          way["amenity"="casino"](area.searchArea);

          node["amenity"="stripclub"](area.searchArea);
          way["amenity"="stripclub"](area.searchArea);

          node["amenity"="gambling"](area.searchArea);
          way["amenity"="gambling"](area.searchArea);

          node["amenity"="events_venue"](area.searchArea);
          way["amenity"="events_venue"](area.searchArea);

          node["amenity"="community_centre"](area.searchArea);
          way["amenity"="community_centre"](area.searchArea);

          node["amenity"="food_court"](area.searchArea);
          way["amenity"="food_court"](area.searchArea);

          node["amenity"="fast_food"](area.searchArea);
          way["amenity"="fast_food"](area.searchArea);

          node["leisure"="dance"](area.searchArea);
          way["leisure"="dance"](area.searchArea);

          node["leisure"="adult_gaming_centre"](area.searchArea);
          way["leisure"="adult_gaming_centre"](area.searchArea);

          node["shop"="alcohol"](area.searchArea);
          way["shop"="alcohol"](area.searchArea);

          node["shop"="convenience"](area.searchArea);
          way["shop"="convenience"](area.searchArea);

          node["shop"="beverages"](area.searchArea);
          way["shop"="beverages"](area.searchArea);

          node["shop"="wine"](area.searchArea);
          way["shop"="wine"](area.searchArea);

          // AMPLIAÇÃO: busca por nome (regex, case-insensitive) para
          // pegar estabelecimentos informais que não têm tag amenity/shop
          // "oficial" mas têm esses termos no nome — comum em barracas de
          // churrasquinho/espetinho e tabernas de bairro em Belém.
          node["name"~"taberna|churrasquinho|churrasco|assados|espeto|espetinho",i](area.searchArea);
          way["name"~"taberna|churrasquinho|churrasco|assados|espeto|espetinho",i](area.searchArea);
        );
        out center;
        """

    headers = {
        "User-Agent": "MapeamentoBelemBot/1.0 (meu_email_ou_projeto@email.com)",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    print("Enviando requisição para a Overpass API (OpenStreetMap)...")

    # CORREÇÃO 2: inicializar response=None antes do try.
    # Do jeito que estava, se requests.post() falhasse antes de retornar
    # (timeout, erro de conexão, etc.), a variável 'response' nunca seria
    # criada e o bloco except quebraria com UnboundLocalError ao tentar
    # acessar response.text.
    response = None
    try:
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

        # CORREÇÃO 3: a categoria estava sendo lida só de tags["amenity"].
        # Lojas de conveniência e depósitos de bebida no OSM são marcados
        # com a tag "shop", não "amenity" — por isso ficavam com
        # categoria=None e depois desapareciam no .map() de tradução.
        # AMPLIAÇÃO: leisure=dance e leisure=adult_gaming_centre usam a
        # tag "leisure", então ela também entra na checagem.
        categoria_bruta = (
            tags.get("amenity") or tags.get("shop") or tags.get("leisure")
        )

        # AMPLIAÇÃO: locais capturados só pela busca de nome (regex de
        # churrasquinho/taberna/espeto/etc.) podem não ter nenhuma tag
        # amenity/shop/leisure — sem isso, ficariam com categoria=None e
        # "sumiriam" no CSV. Marcamos como categoria informal explícita.
        if categoria_bruta is None:
            categoria_bruta = "informal_por_nome"

        info = {
            "id": elem.get("id"),
            "nome": tags.get("name", "Sem Nome Registrado"),
            "categoria": categoria_bruta,
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

    # CORREÇÃO 4: adicionado "convenience" ao dicionário de tradução,
    # já que agora essa categoria também é coletada.
    traducao_categorias = {
        "restaurant": "Restaurante",
        "bar": "Bar",
        "pub": "Pub/Bar",
        "cafe": "Café",
        "biergarten": "Cervejaria ao Ar Livre",
        "nightclub": "Casa de Show/Boate",
        "casino": "Casino",
        "stripclub": "Casa Noturna Adulta",
        "gambling": "Casa de Jogos/Bingo",
        "events_venue": "Espaço de Eventos",
        "community_centre": "Centro Comunitário",
        "food_court": "Praça de Alimentação",
        "fast_food": "Fast Food/Lanchonete",
        "dance": "Salão de Dança/Forró",
        "adult_gaming_centre": "Fliperama/Casa de Jogos",
        "alcohol": "Depósito de Bebidas",
        "convenience": "Loja de Conveniência",
        "beverages": "Depósito de Bebidas",
        "wine": "Loja de Vinhos",
        "informal_por_nome": "Estabelecimento Informal (Churrasquinho/Taberna)",
    }
    # CORREÇÃO 5: usar .map(...).fillna(categoria_bruta) em vez de só
    # .map(...), para que categorias não previstas no dicionário não virem
    # NaN silenciosamente (mantém o valor original em vez de sumir).
    df["categoria"] = df["categoria"].map(traducao_categorias).fillna(df["categoria"])

    return df


if __name__ == "__main__":
    df_locais = coletar_estabelecimentos_belem()

    if df_locais is not None and not df_locais.empty:
        csv_filename = "estabelecimentos_belem2.csv"
        df_locais.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        print(f"Dados salvos com sucesso em: {csv_filename}")

        print("\nResumo por Categoria:")
        print(df_locais["categoria"].value_counts())

        print("\nExemplo dos primeiros dados coletados:")
        print(df_locais[["nome", "categoria", "bairro"]].head())
    else:
        print("Nenhum dado foi gerado ou a base retornou vazia.")