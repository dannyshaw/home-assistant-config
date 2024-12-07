import logging

import homeassistant.helpers.config_validation as cv
import openai
import voluptuous as vol
from homeassistant.components.notify import (
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

CONF_PROMPT_TEMPLATES = "prompt_templates"
CONF_TTS_SERVICE = "tts_service"
CONF_DEFAULT_MEDIA_PLAYER = "default_media_player"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_TTS_SERVICE, default="tts.google_translate_say"): cv.string,
        vol.Optional(CONF_DEFAULT_MEDIA_PLAYER): cv.string,
        vol.Optional(CONF_PROMPT_TEMPLATES, default={}): {
            cv.string: cv.string  # template_name: prompt_template
        },
    }
)


def get_service(hass, config, discovery_info=None):
    """Get the AI Notify service."""
    api_key = config[CONF_API_KEY]
    tts_service = config[CONF_TTS_SERVICE]
    default_media_player = config.get(CONF_DEFAULT_MEDIA_PLAYER)
    prompt_templates = config[CONF_PROMPT_TEMPLATES]
    return AINotifyService(
        api_key, tts_service, default_media_player, prompt_templates, hass
    )


class AINotifyService(BaseNotificationService):
    """Implementation of a notification service that uses OpenAI."""

    def __init__(
        self, api_key, tts_service, default_media_player, prompt_templates, hass
    ):
        """Initialize the service."""
        self.api_key = api_key
        self.tts_service = tts_service
        self.default_media_player = default_media_player
        self.prompt_templates = prompt_templates
        self.hass = hass
        openai.api_key = self.api_key

    def send_message(self, message="", **kwargs):
        """Send a message to a user."""
        data = kwargs.get("data", {})
        media_player = data.get("media_player", self.default_media_player)
        prompt_template_name = data.get("prompt_template", "default")
        prompt_template = self.prompt_templates.get(
            prompt_template_name,
            "Please rephrase the following message in a creative way: '{message}'",
        )
        tts_service = data.get("tts_service", self.tts_service)

        if not media_player:
            _LOGGER.error("No media player specified or configured.")
            return

        # Generate the rephrased message
        try:
            prompt = prompt_template.format(message=message)
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=60,
                temperature=0.9,
            )
            new_message = response.choices[0].text.strip()
            _LOGGER.debug(f"Original message: '{message}'")
            _LOGGER.debug(f"Generated message: '{new_message}'")
        except Exception as e:
            _LOGGER.error(f"Error communicating with OpenAI: {e}")
            new_message = message  # Fallback to the original message

        # Send the rephrased message using the specified TTS service
        self.hass.services.call(
            "tts",
            tts_service.split(".")[1],
            {
                "entity_id": media_player,
                "message": new_message,
            },
        )
