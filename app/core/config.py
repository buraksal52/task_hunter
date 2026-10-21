from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./data/hunter.db"
    telegram_bot_token: SecretStr | None = None
    telegram_webhook_secret: SecretStr | None = None
    telegram_allowed_user_id: int | None = None
    telegram_allowed_chat_id: int | None = None
    admin_api_key: SecretStr | None = None
    app_timezone: str = "Europe/Istanbul"
    collection_enabled: bool = False
    daily_report_hour: int = Field(default=18, ge=0, le=23)

    def validate_production(self) -> None:
        if self.app_env == "production":
            required = {
                "TELEGRAM_BOT_TOKEN": self.telegram_bot_token,
                "TELEGRAM_WEBHOOK_SECRET": self.telegram_webhook_secret,
                "TELEGRAM_ALLOWED_USER_ID": self.telegram_allowed_user_id,
                "TELEGRAM_ALLOWED_CHAT_ID": self.telegram_allowed_chat_id,
                "ADMIN_API_KEY": self.admin_api_key,
            }
            missing = [name for name, value in required.items() if value in (None, "")]
            if missing:
                raise ValueError(f"Missing production configuration: {', '.join(missing)}")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
