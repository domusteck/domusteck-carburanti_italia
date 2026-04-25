from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .api import CarburantiItaliaAPI
from .coordinator import CarburantiItaliaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup dell'integrazione tramite ConfigEntry."""

    # Inizializza API con i parametri della config entry
    api = CarburantiItaliaAPI(
        city=entry.data.get("city"),
        province=entry.data.get("province"),
        fuel_type=entry.data.get("fuel_type"),
        radius=entry.data.get("radius", 15),
    )

    # Coordinator
    coordinator = CarburantiItaliaCoordinator(hass, entry, api)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Primo aggiornamento dati
    await coordinator.async_refresh()

    # ---------------------------------------------------------
    # SERVIZIO: dump_api
    # ---------------------------------------------------------
    async def handle_dump_api(call: ServiceCall):
        """Dump dei dati grezzi dell'API nei log."""
        try:
            session = async_get_clientsession(hass)

            data = await api.search_stations(
                session=session,
                city=entry.data.get("city"),
                province=entry.data.get("province"),
                fuel_type=entry.data.get("fuel_type"),
                radius=entry.data.get("radius", 15),
            )

            _LOGGER.warning("Dump API (raw data): %s", data)

        except Exception as e:
            _LOGGER.error("Errore dump_api: %s", e)

    # ---------------------------------------------------------
    # SERVIZIO: refresh_ids
    # ---------------------------------------------------------
    async def handle_refresh_ids(call: ServiceCall):
        """Aggiorna manualmente i dati delle stazioni."""
        _LOGGER.info("Esecuzione refresh manuale Carburanti Italia...")
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "dump_api", handle_dump_api)
    hass.services.async_register(DOMAIN, "refresh_ids", handle_refresh_ids)

    # ---------------------------------------------------------

    # Carica le piattaforme
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Rimuove l'integrazione."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
