from __future__ import annotations

import logging
import aiohttp

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CarburantiItaliaCoordinator(DataUpdateCoordinator):
    """Coordinator per l'integrazione Carburanti Italia."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api):
        """Inizializza il coordinatore."""
        self.hass = hass
        self.entry = entry
        self.api = api  # API come oggetto

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # aggiornamento manuale
        )

    async def _async_update_data(self):
        """Aggiorna i dati chiamando l'API filtrata."""

        city = self.entry.data.get("city")
        province = self.entry.data.get("province")
        fuel_type = self.entry.data.get("fuel_type")

        try:
            async with aiohttp.ClientSession() as session:
                stations = await self.api.search_stations(
                    session, city, province, fuel_type
                )
                return stations  # <-- LISTA, non dict

        except Exception as err:
            raise UpdateFailed(f"Errore aggiornamento dati: {err}") from err
