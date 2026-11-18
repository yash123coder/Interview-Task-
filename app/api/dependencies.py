
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings


hermes_api_key_header = APIKeyHeader(
    name="X-Hermes-API-Key",
    auto_error=False
)


def verify_hermes_api_key(
    api_key: str | None = Depends(hermes_api_key_header)
):
    configured_key = settings.HERMES_API_KEY

    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hermes API authentication is not configured"
        )

    if not api_key or not secrets.compare_digest(
        api_key,
        configured_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Hermes API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return "hermes_agent"
