from __future__ import annotations

import logging
import aiohttp
from datetime import timedelta, datetime

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, UPDATE_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)


class CarburantiItaliaCoordinator(DataUpdateCoordinator):
    """Coordinator per l'integrazione Carburanti Italia."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api):
        """Inizializza il coordinatore."""
        self.hass = hass
        self.entry = entry
        self.api = api

        # Timestamp dell'ultimo aggiornamento riuscito
        self.last_update_success_time: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )

    async def _async_update_data(self):
        """Aggiorna i dati chiamando l'API filtrata."""

        city = self.entry.data.get("city")
        province = self.entry.data.get("province")
        fuel_type = self.entry.data.get("fuel_type")

        try:
            async with aiohttp.ClientSession() as session:
                stations = await self.api.search_stations(
                    session=session,
                    city=city,
                    province=province,
                    fuel_type=fuel_type,
                    radius=15  # raggio fisso 15 km
                )

                if not isinstance(stations, list):
                    raise UpdateFailed("Formato dati non valido: attesa lista di stazioni.")

                # Aggiorniamo il timestamp SOLO se il refresh è riuscito
                self.last_update_success_time = datetime.now()

                return stations

        except Exception as err:
            raise UpdateFailed(f"Errore aggiornamento dati: {err}") from err
