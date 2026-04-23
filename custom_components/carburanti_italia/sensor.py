from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.location import distance

from .const import DOMAIN


# ---------------------------------------------------------
# 🔥 FUNZIONE FILTRO GPS
# ---------------------------------------------------------
def filter_stations(hass, stations):
    """Filtra stazioni per distanza da casa."""

    try:
        home_lat = float(hass.states.get("input_number.lat_casa").state)
        home_lon = float(hass.states.get("input_number.lon_casa").state)
        raggio = float(hass.states.get("input_number.raggio_ricerca_km").state)
    except:
        return stations  # fallback se helper non esistono

    filtered = []

    for s in stations:
        lat = s.get("lat")
        lon = s.get("lon")

        if lat and lon:
            d = distance(home_lat, home_lon, lat, lon)

            if d <= raggio:
                s["distance_km"] = round(d, 2)
                filtered.append(s)

    # 🔥 ordinamento smart (prezzo + distanza)
    filtered.sort(key=lambda x: (x.get("price", 999), x.get("distance_km", 999)))

    return filtered


# ---------------------------------------------------------
# SETUP ENTRY
# ---------------------------------------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup dei sensori tramite ConfigEntry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    city = entry.data.get("city")

    entities = []

    entities.append(CarburantiItaliaCountSensor(coordinator, city))
    entities.append(CarburantiItaliaTop20Sensor(coordinator, city))

    for i in range(20):
        entities.append(CarburantiItaliaStationSensor(coordinator, city, i))

    async_add_entities(entities)


# ---------------------------------------------------------
# SENSOR: NUMERO STAZIONI
# ---------------------------------------------------------
class CarburantiItaliaCountSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, city):
        super().__init__(coordinator)
        self._attr_name = f"Carburanti {city} Numero Stazioni"
        self._attr_unique_id = f"{DOMAIN}_{city}_count"

    @property
    def native_value(self):
        stations = filter_stations(self.hass, self.coordinator.data or [])
        return len(stations)

    @property
    def extra_state_attributes(self):
        stations = filter_stations(self.hass, self.coordinator.data or [])
        return {"count": len(stations)}

    @property
    def icon(self):
        return "mdi:gas-station"


# ---------------------------------------------------------
# SENSOR: TOP 20
# ---------------------------------------------------------
class CarburantiItaliaTop20Sensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, city):
        super().__init__(coordinator)
        self._attr_name = f"Carburanti {city} Top 20"
        self._attr_unique_id = f"{DOMAIN}_{city}_top20"

    @property
    def native_value(self):
        stations = filter_stations(self.hass, self.coordinator.data or [])
        return len(stations)

    @property
    def extra_state_attributes(self):
        stations = filter_stations(self.hass, self.coordinator.data or [])

        reduced = [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "price": s.get("price"),
                "address": s.get("address"),
                "distance_km": s.get("distance_km"),
            }
            for s in stations
        ]

        return {"stations": reduced}

    @property
    def icon(self):
        return "mdi:gas-station"


# ---------------------------------------------------------
# SENSOR: STAZIONE SINGOLA
# ---------------------------------------------------------
class CarburantiItaliaStationSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, city, index):
        super().__init__(coordinator)
        self.index = index
        self._attr_name = f"{city} Stazione {index + 1}"
        self._attr_unique_id = f"{DOMAIN}_{city}_station_{index}"

    @property
    def native_value(self):
        stations = filter_stations(self.hass, self.coordinator.data or [])

        if self.index < len(stations):
            s = stations[self.index]

            price = s.get("price")
            name = s.get("name", "Sconosciuta")
            address = s.get("address", "")
            dist = s.get("distance_km")

            if price is not None:
                if address:
                    return f"{price} € — {name} ({address}) [{dist} km]"
                else:
                    return f"{price} € — {name} [{dist} km]"

        return None

    @property
    def extra_state_attributes(self):
        stations = filter_stations(self.hass, self.coordinator.data or [])

        if self.index < len(stations):
            return stations[self.index]

        return {}

    @property
    def icon(self):
        return "mdi:gas-station"
