import requests
from typing import Optional

print("USING PHOTON GEOCODER")

GEOCODE_URL = "https://photon.komoot.io/api/"
REVERSE_URL = "https://photon.komoot.io/reverse"

# Photon roda sobre a infra do OSM. Mandar um User-Agent identificável
# evita bloqueio/throttling no servidor público de demonstração
# (a doc do Photon pede "uso justo" do endpoint público).
_session = requests.Session()
_session.headers.update({
    "User-Agent": "MeuApp-Geocoder/1.0 (contato@example.com)"
})


def _build_address(props: dict, fallback: Optional[str] = None) -> Optional[str]:
    """
    Monta um endereço legível a partir das properties retornadas pelo Photon.
    Cai para 'name' e depois para 'fallback' se não houver componentes suficientes.
    """
    parts = [
        props.get("street"),
        props.get("housenumber"),
        props.get("district") or props.get("suburb"),
        props.get("city"),
        props.get("state"),
        props.get("country"),
    ]
    address = ", ".join(p for p in parts if p)
    return address or props.get("name") or fallback


def geocode_address(address: str) -> Optional[dict]:
    """
    Converte endereço em coordenadas usando Photon.
    Retorna None se não encontrar resultado ou se a requisição falhar.
    """
    query = f"{address}, Belém, Pará, Brasil"

    params = {
        "q": query,
        "limit": 1,
        "lat": -1.4558,   # bias geográfico (Belém)
        "lon": -48.4892,
    }

    try:
        r = _session.get(GEOCODE_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        print("Photon geocode error (requisição):", e)
        return None
    except ValueError as e:
        print("Photon geocode error (resposta não é JSON):", e)
        return None

    features = data.get("features")
    if not features:
        return None

    feat = features[0]
    try:
        lon, lat = feat["geometry"]["coordinates"]
        props = feat["properties"]
    except (KeyError, ValueError) as e:
        print("Photon geocode error (formato inesperado na resposta):", e)
        return None

    return {
        "lat": lat,
        "lon": lon,
        "address": _build_address(props, fallback=query),
    }


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Converte coordenadas em endereço (Photon reverse).
    Retorna None se não encontrar resultado ou se a requisição falhar.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
    }

    try:
        r = _session.get(REVERSE_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        print("Photon reverse error (requisição):", e)
        return None
    except ValueError as e:
        print("Photon reverse error (resposta não é JSON):", e)
        return None

    features = data.get("features")
    if not features:
        return None

    props = features[0].get("properties", {})
    return _build_address(props)


if __name__ == "__main__":
    # Teste rápido (precisa de internet liberada para photon.komoot.io)
    resultado = geocode_address("Av. Presidente Vargas, 100")
    print("Geocode:", resultado)

    if resultado:
        endereco = reverse_geocode(resultado["lat"], resultado["lon"])
        print("Reverse:", endereco)