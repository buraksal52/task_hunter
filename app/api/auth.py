import secrets

from fastapi import Header, HTTPException, status

from app.core.config import Settings


def require_admin(settings: Settings, x_api_key: str | None) -> None:
    expected = settings.admin_api_key.get_secret_value() if settings.admin_api_key else None
    if not expected or not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def admin_header(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str | None:
    return x_api_key
