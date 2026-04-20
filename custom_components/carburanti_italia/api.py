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


class CarburantiItaliaAPI:
    """API wrapper per Carburanti Italia."""

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
    # PULIZIA INDIRIZZO (mantiene civico, via, città)
    # ---------------------------------------------------------
    def clean_address(self, address: str) -> str:
        if not address:
            return "Indirizzo non disponibile"

        parts = [p.strip() for p in address.split(",")]

        # Caso: civico, via, città, provincia, CAP, Italia
        if len(parts) >= 3:
            civico = parts[0]
            via = parts[1]
            citta = parts[2]

            # Se il civico è numerico (es. "62")
            if civico.replace(" ", "").isdigit():
                return f"{civico}, {via}, {citta}"

            # Se il civico è dentro la via (es. "Via Roma 12")
            if any(char.isdigit() for char in via):
                return f"{via}, {citta}"

            # Caso generico
            return f"{via}, {citta}"

        # Caso: via + città
        if len(parts) == 2:
            return f"{parts[0]}, {parts[1]}"

        return address

    # ---------------------------------------------------------
    # GEOCODING città
    # ---------------------------------------------------------
    async def geocode_city(self, session, city, province):
        headers = {
            "User-Agent": "CarburantiItaliaHomeAssistant/1.0"
        }

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
    # REVERSE GEOCODING (solo se necessario)
    # ---------------------------------------------------------
    async def reverse_geocode(self, session, lat, lon):
        headers = {
            "User-Agent": "CarburantiItaliaHomeAssistant/1.0"
        }

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
    async def search_stations(self, session, city, province, fuel_type):
        if fuel_type not in FUEL_ID_MAP:
            raise ValueError(f"Carburante non supportato: {fuel_type}")

        target_fuel_id = FUEL_ID_MAP[fuel_type]
        api_fuel_type = FUEL_TYPE_MAP[fuel_type]

        # Carica cache indirizzi
        cache = self.load_cache()

        lat, lng = await self.geocode_city(session, city, province)

        payload = {
            "points": [{"lat": lat, "lng": lng}],
            "fuelType": api_fuel_type,
            "priceOrder": "asc",
            "radius": 5
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

            # ---------------------------------------------------------
            # TUTTI i possibili campi indirizzo del MISE
            # ---------------------------------------------------------
            address = (
                item.get("address")
                or item.get("descVia")
                or item.get("descIndirizzo")
                or item.get("via")
                or item.get("indirizzo")
            )

            # Se esiste → pulisci
            if address:
                address = self.clean_address(address)

            # ---------------------------------------------------------
            # SE MANCANTE → CACHE o GEOCODING
            # ---------------------------------------------------------
            if not address:
                if station_id in cache:
                    address = cache[station_id]
                else:
                    lat_s = item["location"]["lat"]
                    lon_s = item["location"]["lng"]

                    await asyncio.sleep(2)  # delay sicurezza

                    raw_address = await self.reverse_geocode(session, lat_s, lon_s)
                    address = self.clean_address(raw_address)

                    cache[station_id] = address
                    self.save_cache(cache)

            stations.append({
                "id": station_id,
                "name": item.get("name"),
                "brand": item.get("brand"),
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
