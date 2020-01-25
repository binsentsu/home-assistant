"""Provide configuration end points for scripts."""
from homeassistant.components.script import DOMAIN, SCRIPT_ENTRY_SCHEMA
from homeassistant.config import SCRIPT_CONFIG_PATH
from homeassistant.const import SERVICE_RELOAD
from homeassistant.helpers import config_validation as cv, entity_registry

from . import ACTION_DELETE, EditKeyBasedConfigView


async def async_setup(hass):
    """Set up the script config API."""

    async def hook(action, config_key):
        """post_write_hook for Config View that reloads scripts."""
        await hass.services.async_call(DOMAIN, SERVICE_RELOAD)

        if action != ACTION_DELETE:
            return

        ent_reg = await entity_registry.async_get_registry(hass)

        entity_id = ent_reg.async_get_entity_id(DOMAIN, DOMAIN, config_key)

        if entity_id is None:
            return

        ent_reg.async_remove(entity_id)

    hass.http.register_view(
        EditKeyBasedConfigView(
            "script",
            "config",
            SCRIPT_CONFIG_PATH,
            cv.slug,
            SCRIPT_ENTRY_SCHEMA,
            post_write_hook=hook,
        )
    )
    return True
