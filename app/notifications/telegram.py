from typing import Any

import httpx

from app.core.config import Settings


class TelegramSender:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client

    async def send_message(self, chat_id: int, text: str) -> dict[str, Any]:
        if not self.settings.telegram_bot_token:
            raise RuntimeError("Telegram is not configured")
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token.get_secret_value()}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if self.client:
            response = await self.client.post(url, json=payload, timeout=10)
        else:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
