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

    entities = []

    # Sensore numero stazioni
    entities.append(CarburantiItaliaCountSensor(coordinator, city))

    # Sensore top 20 (versione leggera)
    entities.append(CarburantiItaliaTop20Sensor(coordinator, city))

    # Sensori stazione 1–20
    for i in range(20):
        entities.append(CarburantiItaliaStationSensor(coordinator, city, i))

    async_add_entities(entities)


# ---------------------------------------------------------
# SENSOR: NUMERO STAZIONI (LEGGERO)
# ---------------------------------------------------------
class CarburantiItaliaCountSensor(CoordinatorEntity, SensorEntity):
    """Numero totale di stazioni trovate."""

    def __init__(self, coordinator, city):
        super().__init__(coordinator)
        self._attr_name = f"Carburanti {city} Numero Stazioni"
        self._attr_unique_id = f"{DOMAIN}_{city}_count"

    @property
    def native_value(self):
        stations = self.coordinator.data or []
        return len(stations)

    @property
    def extra_state_attributes(self):
        stations = self.coordinator.data or []
        return {
            "count": len(stations)
        }

    @property
    def icon(self):
        return "mdi:gas-station"


# ---------------------------------------------------------
# SENSOR: TOP 20 (VERSIONE MEDIA, ATTRIBUTI RIDOTTI)
# ---------------------------------------------------------
class CarburantiItaliaTop20Sensor(CoordinatorEntity, SensorEntity):
    """Restituisce la lista delle stazioni in forma ridotta."""

    def __init__(self, coordinator, city):
        super().__init__(coordinator)
        self._attr_name = f"Carburanti {city} Top 20"
        self._attr_unique_id = f"{DOMAIN}_{city}_top20"

    @property
    def native_value(self):
        stations = self.coordinator.data or []
        return len(stations)

    @property
    def extra_state_attributes(self):
        stations = self.coordinator.data or []

        # Lista ridotta per evitare superamento 16 KB
        reduced = [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "price": s.get("price"),
                "address": s.get("address")
            }
            for s in stations
        ]

        return {"stations": reduced}

    @property
    def icon(self):
        return "mdi:gas-station"


# ---------------------------------------------------------
# SENSOR: STAZIONE SINGOLA (1–20)
# ---------------------------------------------------------
class CarburantiItaliaStationSensor(CoordinatorEntity, SensorEntity):
    """Sensore per una singola stazione (prezzo + nome + indirizzo breve)."""

    def __init__(self, coordinator, city, index):
        super().__init__(coordinator)
        self.index = index
        self._attr_name = f"{city} Stazione {index + 1}"
        self._attr_unique_id = f"{DOMAIN}_{city}_station_{index}"

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
                else:
                    return f"{price} € — {name}"

        return None

    @property
    def extra_state_attributes(self):
        stations = self.coordinator.data or []

        if self.index < len(stations):
            return stations[self.index]

        return {}

    @property
    def icon(self):
        return "mdi:gas-station"
