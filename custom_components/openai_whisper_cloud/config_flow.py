from __future__ import annotations
import asyncio
from typing import Any
import requests
import voluptuous as vol
from homeassistant import exceptions
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_MODEL, CONF_NAME
import homeassistant.helpers.config_validation as cv
from . import _LOGGER
from .const import (
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_LINK,  # 导入 CONF_LINK
    DEFAULT_NAME,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_WHISPER_MODEL,
    DOMAIN,
    SUPPORTED_MODELS,
)

# URL 验证函数
def url_validator(url: str) -> str:
    """验证 URL 格式，确保以 http:// 或 https:// 开头，且末尾不包含 /。"""
    if not (url.startswith("http://") or url.startswith("https://")):
        raise vol.Invalid("URL 必须以 http:// 或 https:// 开头")
    if url.endswith("/"):
        raise vol.Invalid("URL 末尾不应包含 /")
    return url

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,  # 必填项：名称
        vol.Required(CONF_LINK, default=""): cv.string,  # 必填项：自定义 API 链接
        vol.Required(CONF_API_KEY): cv.string,  # 必填项：API 密钥
        vol.Required(CONF_MODEL, default=DEFAULT_WHISPER_MODEL): vol.In(SUPPORTED_MODELS),  # 必填项：模型选择
        vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.All(  # 可选项：温度参数
            vol.Coerce(float), vol.Range(min=0, max=1)
        ),
        vol.Optional(CONF_PROMPT): cv.string,  # 可选项：提示文本
    }
)

async def validate_input(data: dict):
    """验证用户输入的 API 密钥和模型。"""
    obscured_api_key = data.get(CONF_API_KEY)
    data[CONF_API_KEY] = "<api_key>"
    _LOGGER.debug("用户输入验证中：%s", data)
    data[CONF_API_KEY] = obscured_api_key

    # 固定的 API URL，只用于 API 验证
    api_url = "https://api.groq.com/openai/v1/models"

    # 异步发送 GET 请求以验证 API 密钥和模型
    response = await asyncio.to_thread(
        requests.get,
        url=api_url,
        headers={
            "Authorization": f"Bearer {data.get(CONF_API_KEY)}",
            "Content-Type": "application/json"
        },
    )

    _LOGGER.debug("模型请求耗时 %f 秒，返回状态码 %d - %s",
                   response.elapsed.total_seconds(), response.status_code, response.reason)

    if response.status_code == 401:
        _LOGGER.error("无效的 API 密钥")
        raise InvalidAPIKey  # 无效 API 密钥

    if response.status_code == 403:
        _LOGGER.error("未授权的访问")
        raise UnauthorizedError  # 未授权访问

    if response.status_code != 200:
        _LOGGER.error("未知错误，状态码: %d", response.status_code)
        raise UnknownError  # 其他非 200 状态码

    models = response.json().get("data", [])
    if not any(model.get("id") == data.get(CONF_MODEL) for model in models):
        _LOGGER.error("未找到指定的 Whisper 模型")
        raise WhisperModelNotFound  # 模型未找到

    _LOGGER.debug("用户输入验证成功")  # 验证成功

class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """处理 UI 配置流。"""
    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """处理初始步骤。"""
        errors = {}
        if user_input is not None:
            try:
                # 验证 URL
                url_validator(user_input.get(CONF_LINK, ""))
                
                # 验证输入
                await validate_input(user_input)
                _LOGGER.info("配置创建成功：%s", user_input.get(CONF_NAME, DEFAULT_NAME))
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME), data=user_input
                )

            except requests.exceptions.RequestException as e:
                _LOGGER.error("连接错误：%s", e)
                errors["base"] = "connection_error"
            except UnauthorizedError:
                _LOGGER.error("未经授权的访问")
                errors["base"] = "unauthorized"
            except InvalidAPIKey:
                _LOGGER.error("无效的 API 密钥")
                errors[CONF_API_KEY] = "invalid_api_key"
            except WhisperModelNotFound:
                _LOGGER.error("未找到 Whisper 模型")
                errors["base"] = "whisper_model_not_found"
            except UnknownError:
                _LOGGER.error("发生未知错误")
                errors["base"] = "unknown"
            except vol.Invalid as e:
                _LOGGER.error("URL 验证失败：%s", e)
                errors[CONF_LINK] = str(e)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None):
        """处理 UI 重新配置流。"""
        config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if not config_entry:
            _LOGGER.error("重新配置失败，未找到配置条目")
            return self.async_abort(reason="reconfigure_failed")

        suggested_values = user_input or config_entry.data

        errors = {}
        if user_input is not None:
            try:
                # 验证 URL
                url_validator(user_input.get(CONF_LINK, ""))
                
                # 验证输入
                await validate_input(user_input)
                _LOGGER.info("重新配置成功：%s", user_input.get(CONF_NAME, DEFAULT_NAME))
                return self.async_update_reload_and_abort(
                    config_entry,
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    unique_id=config_entry.unique_id,
                    data=user_input,
                    reason="reconfigure_successful",
                )

            except requests.exceptions.RequestException as e:
                _LOGGER.error("连接错误：%s", e)
                errors["base"] = "connection_error"
            except UnauthorizedError:
                _LOGGER.error("未经授权的访问")
                errors["base"] = "unauthorized"
            except InvalidAPIKey:
                _LOGGER.error("无效的 API 密钥")
                errors[CONF_API_KEY] = "invalid_api_key"
            except WhisperModelNotFound:
                _LOGGER.error("未找到 Whisper 模型")
                errors["base"] = "whisper_model_not_found"
            except UnknownError:
                _LOGGER.error("发生未知错误")
                errors["base"] = "unknown"
            except vol.Invalid as e:
                _LOGGER.error("URL 验证失败：%s", e)
                errors[CONF_LINK] = str(e)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                data_schema=STEP_USER_DATA_SCHEMA, suggested_values=suggested_values
            ),
            errors=errors,
        )
