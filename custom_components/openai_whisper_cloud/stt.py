from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable
import io
import wave

import requests

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
    SpeechToTextEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SUPPORTED_LANGUAGES, CONF_LINK

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置通过配置条目的语音转文本平台。"""
    config_data = {
        "api_key": config_entry.data.get("api_key"),
        "model": config_entry.data.get("model"),
        "temperature": config_entry.data.get("temperature"),
        "prompt": config_entry.data.get("prompt"),
        "name": config_entry.data.get("name"),
        "unique_id": config_entry.entry_id,
        "link": config_entry.data.get(CONF_LINK, ""),
    }

    async_add_entities([GroqWhisperCloudEntity(**config_data)])

class GroqWhisperCloudEntity(SpeechToTextEntity):
    """GroqCloud Whisper API 实体。"""

    def __init__(self, api_key, model, temperature, prompt, name, unique_id, link) -> None:
        """初始化语音转文本服务。"""
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.prompt = prompt
        self._attr_name = name
        self._attr_unique_id = unique_id
        self.link = link
        self._attr_state = "就绪"

    @property
    def state(self) -> str:
        """返回实体的当前状态。"""
        return self._attr_state

    @property
    def supported_languages(self) -> list[str]:
        """返回支持的语言列表。"""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """返回支持的格式列表。"""
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """返回支持的编解码器列表。"""
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """返回支持的比特率列表。"""
        return [
            AudioBitRates.BITRATE_8,
            AudioBitRates.BITRATE_16,
            AudioBitRates.BITRATE_24,
            AudioBitRates.BITRATE_32,
        ]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """返回支持的采样率列表。"""
        return [
            AudioSampleRates.SAMPLERATE_8000,
            AudioSampleRates.SAMPLERATE_16000,
            AudioSampleRates.SAMPLERATE_44100,
            AudioSampleRates.SAMPLERATE_48000,
        ]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """返回支持的声道列表。"""
        return [AudioChannels.CHANNEL_MONO, AudioChannels.CHANNEL_STEREO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        """处理音频流到语音转文本服务。"""
        self._attr_state = "处理中"
        self.async_write_ha_state()

        data = b""
        async for chunk in stream:
            data += chunk
            if len(data) / (1024 * 1024) > 24.5:
                self._attr_state = "错误：音频流大小超过25MB限制"
                self.async_write_ha_state()
                return SpeechResult("", SpeechResultState.ERROR)

        if not data:
            self._attr_state = "错误：未收到音频数据"
            self.async_write_ha_state()
            return SpeechResult("", SpeechResultState.ERROR)

        try:
            temp_file = io.BytesIO()
            with wave.open(temp_file, "wb") as wav_file:
                wav_file.setnchannels(metadata.channel)
                wav_file.setframerate(metadata.sample_rate)
                wav_file.setsampwidth(2)
                wav_file.writeframes(data)

            temp_file.seek(0)

            files = {
                "file": ("audio.wav", temp_file, "audio/wav"),
            }

            data = {
                "model": self.model,
                "language": metadata.language,
                "temperature": self.temperature,
                "prompt": self.prompt,
                "response_format": "json"
            }

            response = await asyncio.to_thread(
                requests.post,
                f"{self.link}/openai/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                files=files,
                data=data
            )

            transcription = response.json().get("text", "")

            if not transcription:
                self._attr_state = "错误：未收到转录结果"
                self.async_write_ha_state()
                return SpeechResult("", SpeechResultState.ERROR)

            self._attr_state = "转录成功"
            self.async_write_ha_state()
            return SpeechResult(transcription, SpeechResultState.SUCCESS)

        except requests.exceptions.RequestException:
            self._attr_state = "错误：请求异常"
            self.async_write_ha_state()
            return SpeechResult("", SpeechResultState.ERROR)
