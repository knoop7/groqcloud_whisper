import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant

from .const import DEFAULT_NAME, CONF_LINK

PLATFORMS = [Platform.STT]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load entry."""
    _LOGGER.info("Setting up %s", entry)
    
    # Forward the entry setup to the configured platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Add an update listener to handle changes to the configuration
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    # Ensure the CONF_LINK is properly set up for other programs
    link = entry.data.get(CONF_LINK, "")
    if link:
        _LOGGER.info("Using proxy link: %s", link)
    else:
        _LOGGER.info("No proxy link configured")
    
    return True

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update entry."""
    _LOGGER.info("Configuration update detected. Reloading entry: %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading %s", entry)
    
    # Unload platforms associated with the entry
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating configuration from version %s.%s", config_entry.version, config_entry.minor_version)
    
    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False
    
    if config_entry.version == 0:
        # Upgrade from version 0 to version 1
        new_data = {**config_entry.data}
        
        # Set default values for new fields if necessary
        new_data.setdefault(CONF_NAME, DEFAULT_NAME)
        new_data.setdefault(CONF_LINK, "")  # Ensure CONF_LINK is present
        
        hass.config_entries.async_update_entry(config_entry, data=new_data, minor_version=0, version=1)
    
    _LOGGER.debug("Migration to configuration version %s.%s successful", config_entry.version, config_entry.minor_version)
    
    return True
