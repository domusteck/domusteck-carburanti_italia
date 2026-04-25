import aiohttp
import logging
import json
import os
import asyncio

API_URL = "https://carburanti.mise.gov.it/ospzApi/search/zone"
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

_LOGGER = logging.getLogger(__name__)

CACHE_FILE = "address_cache.json"

FUEL_ID_MAP = {
    "Benzina": 1,
    "Gasolio": 2,
    "GPL": 4,
    "Metano": 3
}

FUEL_TYPE_MAP = {
    "Benzina": "1-x",
    "Gasolio": "2-x",
    "GPL": "4-x",
    "Metano": "3-x"
}

# ---------------------------------------------------------
# BRAND MAP COMPLETA (con priorità ENI)
# ---------------------------------------------------------
BRAND_MAP = {
    "eni": {"label": "Eni", "logo": "eni.png"},
    "agip": {"label": "Agip", "logo": "agip.png"},
    "ip": {"label": "IP", "logo": "ip.png"},
    "esso": {"label": "Esso", "logo": "esso.png"},
    "tamoil": {"label": "Tamoil", "logo": "tamoil.png"},
    "q8": {"label": "Q8", "logo": "q8.png"},
    "q8easy": {"label": "Q8easy", "logo": "q8easy.png"},
    "energas": {"label": "Energas", "logo": "energas.png"},
    "default": {"label": "Pompa Bianca", "logo": "pompabianca.png"},
}

# ---------------------------------------------------------
# NORMALIZZAZIONE BRAND (priorità ENI)
# ---------------------------------------------------------
def normalize_brand(raw):
    if not raw:
        return BRAND_MAP["default"]

    text = raw.lower()

    for ch in [",", ".", "-", "_"]:
        text = text.replace(ch, " ")

    text = " ".join(text.split())
    parts = text.split(" ")

    if "eni" in parts:
        return BRAND_MAP["eni"]

    if "agip" in parts:
        return BRAND_MAP["agip"]

    for p in parts:
        if p in BRAND_MAP:
            return BRAND_MAP[p]

    return BRAND_MAP["default"]


class CarburantiItaliaAPI:
    """API wrapper per Carburanti Italia."""

    # ---------------------------------------------------------
    # COSTRUTTORE (necessario!)
    # ---------------------------------------------------------
    def __init__(self, city=None, province=None, fuel_type=None, radius=15):
        self.city = city
        self.province = province
        self.fuel_type = fuel_type
        self.radius = radius

    # ---------------------------------------------------------
    # CARICA CACHE
    # ---------------------------------------------------------
    def load_cache(self):
        if not os.path.exists(CACHE_FILE):
            return {}

        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    # ---------------------------------------------------------
    # SALVA CACHE
    # ---------------------------------------------------------
    def save_cache(self, cache):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            _LOGGER.error(f"Errore salvataggio cache indirizzi: {e}")

    # ---------------------------------------------------------
    # PULIZIA INDIRIZZO
    # ---------------------------------------------------------
    def clean_address(self, address: str) -> str:
        if not address:
            return "Indirizzo non disponibile"

        parts = [p.strip() for p in address.split(",")]

        if len(parts) >= 3:
            civico = parts[0]
            via = parts[1]
            citta = parts[2]

            if civico.replace(" ", "").isdigit():
                return f"{civico}, {via}, {citta}"

            if any(char.isdigit() for char in via):
                return f"{via}, {citta}"

            return f"{via}, {citta}"

        if len(parts) == 2:
            return f"{parts[0]}, {parts[1]}"

        return address

    # ---------------------------------------------------------
    # GEOCODING città
    # ---------------------------------------------------------
    async def geocode_city(self, session, city, province):
        headers = {"User-Agent": "CarburantiItaliaHomeAssistant/1.0"}

        params = {
            "q": f"{city} {province}, Italia",
            "format": "json",
            "limit": 1
        }

        async with session.get(GEOCODE_URL, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Errore geocoding: {resp.status}")

            data = await resp.json()

        if not data:
            raise Exception("Impossibile ottenere coordinate per la città.")

        return float(data[0]["lat"]), float(data[0]["lon"])

    # ---------------------------------------------------------
    # REVERSE GEOCODING
    # ---------------------------------------------------------
    async def reverse_geocode(self, session, lat, lon):
        headers = {"User-Agent": "CarburantiItaliaHomeAssistant/1.0"}

        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 18,
            "addressdetails": 1
        }

        async with session.get(REVERSE_URL, params=params, headers=headers) as resp:
            if resp.status != 200:
                return None

            data = await resp.json()

        return data.get("display_name")

    # ---------------------------------------------------------
    # API PRINCIPALE
    # ---------------------------------------------------------
    async def search_stations(self, session, city=None, province=None, fuel_type=None, radius=None):
        """Ricerca stazioni carburante entro un raggio."""

        city = city or self.city
        province = province or self.province
        fuel_type = fuel_type or self.fuel_type
        radius = radius or self.radius

        if fuel_type not in FUEL_ID_MAP:
            raise ValueError(f"Carburante non supportato: {fuel_type}")

        target_fuel_id = FUEL_ID_MAP[fuel_type]
        api_fuel_type = FUEL_TYPE_MAP[fuel_type]

        cache = self.load_cache()

        lat, lng = await self.geocode_city(session, city, province)

        payload = {
            "points": [{"lat": lat, "lng": lng}],
            "fuelType": api_fuel_type,
            "priceOrder": "asc",
            "radius": radius
        }

        async with session.post(API_URL, json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"Errore API: {resp.status}")

            data = await resp.json()

        if not data.get("success"):
            raise Exception("API MISE ha restituito success=false")

        results = data.get("results", [])
        stations = []

        for item in results:
            prices = []

            for f in item.get("fuels", []):
                fid_raw = f.get("fuelId")

                try:
                    fid = int(str(fid_raw).split("-")[0])
                except:
                    continue

                if fid != target_fuel_id:
                    continue

                price = f.get("price")
                if price is None:
                    continue

                prices.append(price)

            if not prices:
                continue

            price = min(prices)
            station_id = str(item.get("id"))

            address = (
                item.get("address")
                or item.get("descVia")
                or item.get("descIndirizzo")
                or item.get("via")
                or item.get("indirizzo")
            )

            if address:
                address = self.clean_address(address)

            if not address:
                if station_id in cache:
                    address = cache[station_id]
                else:
                    lat_s = item["location"]["lat"]
                    lon_s = item["location"]["lng"]

                    await asyncio.sleep(2)

                    raw_address = await self.reverse_geocode(session, lat_s, lon_s)
                    address = self.clean_address(raw_address)

                    cache[station_id] = address
                    self.save_cache(cache)

            brand_info = normalize_brand(item.get("brand"))

            stations.append({
                "id": station_id,
                "name": item.get("name"),
                "brand": brand_info["label"],
                "brand_logo": brand_info["logo"],
                "address": address,
                "price": price,
                "latitude": item["location"]["lat"],
                "longitude": item["location"]["lng"],
                "fuel_type": fuel_type,
                "distance": float(item.get("distance", 0)),
                "fuels": item.get("fuels", [])
            })

        stations.sort(key=lambda x: x["price"])
        return stations
