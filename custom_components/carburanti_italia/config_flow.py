from __future__ import annotations

import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_CITY,
    CONF_PROVINCE,
    CONF_FUEL_TYPE,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_FUELS = [
    "Benzina",
    "Gasolio",
    "GPL",
    "Metano",
]


class CarburantiItaliaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestione del flusso di configurazione."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Primo step: inserimento città, provincia e carburante."""

        errors = {}

        if user_input is not None:
            city = user_input.get(CONF_CITY)
            province = user_input.get(CONF_PROVINCE)
            fuel = user_input.get(CONF_FUEL_TYPE)

            if not city or not province:
                errors["base"] = "invalid_input"
            else:
                # Creiamo un ID unico basato su città + provincia + carburante
                unique_id = f"{city}_{province}_{fuel}".lower().replace(" ", "_")

                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{city} ({province}) - {fuel}",
                    data=user_input
                )

        schema = vol.Schema({
            vol.Required(CONF_CITY): str,
            vol.Required(CONF_PROVINCE): str,
            vol.Required(CONF_FUEL_TYPE): vol.In(SUPPORTED_FUELS),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )


# ---------------------------------------------------------
#   OPTIONS FLOW (per modificare la configurazione)
# ---------------------------------------------------------

class CarburantiItaliaOptionsFlow(config_entries.OptionsFlow):
    """Gestione delle opzioni dell'integrazione."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Modifica città, provincia o carburante."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_CITY, default=self.config_entry.data.get(CONF_CITY)): str,
            vol.Required(CONF_PROVINCE, default=self.config_entry.data.get(CONF_PROVINCE)): str,
            vol.Required(CONF_FUEL_TYPE, default=self.config_entry.data.get(CONF_FUEL_TYPE)): vol.In(SUPPORTED_FUELS),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
