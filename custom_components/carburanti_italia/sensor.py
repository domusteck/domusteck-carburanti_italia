from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


# ---------------------------------------------------------
# SETUP ENTRY
# ---------------------------------------------------------
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup dei sensori tramite ConfigEntry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]

    city = entry.data.get("city")
    fuel_type = entry.data.get("fuel_type")

    entities = []

    # Sensore numero stazioni
    entities.append(CarburantiItaliaCountSensor(coordinator, city, fuel_type))

    # Sensore top 20
    entities.append(CarburantiItaliaTop20Sensor(coordinator, city, fuel_type))

    # Sensori stazione 1–20
    for i in range(20):
        entities.append(CarburantiItaliaStationSensor(coordinator, city, fuel_type, i))

    async_add_entities(entities)


# ---------------------------------------------------------
# SENSOR: NUMERO STAZIONI
# ---------------------------------------------------------
class CarburantiItaliaCountSensor(CoordinatorEntity, SensorEntity):
    """Numero totale di stazioni trovate."""

    def __init__(self, coordinator, city, fuel_type):
        super().__init__(coordinator)
        self.city = city
        self.fuel_type = fuel_type.lower()

        self._attr_name = f"Carburanti {city} {fuel_type} Numero Stazioni"
        self._attr_unique_id = f"{DOMAIN}_{city}_{self.fuel_type}_count"

    @property
    def native_value(self):
        stations = self.coordinator.data or []
        return len(stations)

    @property
    def extra_state_attributes(self):
        return {
            "count": len(self.coordinator.data or []),
            "ultimo_aggiornamento": (
                self.coordinator.last_update_success_time.strftime("%H:%M")
                if self.coordinator.last_update_success_time else None
            )
        }

    @property
    def icon(self):
        return "mdi:gas-station"


# ---------------------------------------------------------
# SENSOR: TOP 20 (ARRICCHITO)
# ---------------------------------------------------------
class CarburantiItaliaTop20Sensor(CoordinatorEntity, SensorEntity):
    """Restituisce la lista delle stazioni in forma ridotta (max 20)."""

    def __init__(self, coordinator, city, fuel_type):
        super().__init__(coordinator)
        self.city = city
        self.fuel_type = fuel_type.lower()

        self._attr_name = f"Carburanti {city} {fuel_type} Top 20"
        self._attr_unique_id = f"{DOMAIN}_{city}_{self.fuel_type}_top20"

    @property
    def native_value(self):
        stations = self.coordinator.data or []
        return min(len(stations), 20)

    @property
    def extra_state_attributes(self):
        stations = (self.coordinator.data or [])[:20]

        # 🔥 VERSIONE PATCHATA: aggiunte latitude e longitude
        reduced = [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "price": s.get("price"),
                "address": s.get("address"),
                "brand": s.get("brand"),
                "brand_logo": s.get("brand_logo"),
                "latitude": s.get("latitude"),
                "longitude": s.get("longitude"),
            }
            for s in stations
        ]

        return {
            "stations": reduced,
            "fuel_type": self.fuel_type,
            "ultimo_aggiornamento": (
                self.coordinator.last_update_success_time.strftime("%H:%M")
                if self.coordinator.last_update_success_time else None
            )
        }

    @property
    def icon(self):
        return "mdi:gas-station"


# ---------------------------------------------------------
# SENSOR: STAZIONE SINGOLA (ARRICCHITO)
# ---------------------------------------------------------
class CarburantiItaliaStationSensor(CoordinatorEntity, SensorEntity):
    """Sensore per una singola stazione (prezzo + nome + indirizzo breve)."""

    def __init__(self, coordinator, city, fuel_type, index):
        super().__init__(coordinator)
        self.city = city
        self.fuel_type = fuel_type.lower()
        self.index = index

        self._attr_name = f"{city} {fuel_type} Stazione {index + 1}"
        self._attr_unique_id = f"{DOMAIN}_{city}_{self.fuel_type}_station_{index}"

    @property
    def native_value(self):
        stations = self.coordinator.data or []

        if self.index < len(stations):
            station = stations[self.index]

            price = station.get("price")
            name = station.get("name", "Sconosciuta")
            address = station.get("address", "")

            if price is not None:
                if address:
                    return f"{price} € — {name} ({address})"
                return f"{price} € — {name}"

        return None

    @property
    def extra_state_attributes(self):
        stations = self.coordinator.data or []

        if self.index < len(stations):
            attrs = stations[self.index].copy()

            # 🔥 Aggiungiamo timestamp
            attrs["ultimo_aggiornamento"] = (
                self.coordinator.last_update_success_time.strftime("%H:%M")
                if self.coordinator.last_update_success_time else None
            )

            return attrs

        return {}

    @property
    def icon(self):
        return "mdi:gas-station"
