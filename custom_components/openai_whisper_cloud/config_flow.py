from __future__ import annotations
import asyncio
from typing import Any
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_NAME
import homeassistant.helpers.config_validation as cv
from .const import (
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_LINK,
    DEFAULT_NAME,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_WHISPER_MODEL,
    DOMAIN,
    SUPPORTED_MODELS,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_LINK, default=""): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_MODEL, default=DEFAULT_WHISPER_MODEL): vol.In(SUPPORTED_MODELS),
        vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=1)
        ),
        vol.Optional(CONF_PROMPT, default=DEFAULT_PROMPT): cv.string,
    }
)

class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """处理配置流程。"""
    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """处理用户输入步骤。"""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, DEFAULT_NAME),
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """处理重新配置步骤。"""
        config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if not config_entry:
            return self.async_abort(reason="entry_not_found")

        if user_input is not None:
            return self.async_update_entry(
                config_entry,
                title=user_input.get(CONF_NAME, DEFAULT_NAME),
                data=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA,
                config_entry.data
            ),
        )
