import os
from typing import Optional, Set

import httpx
from cachetools import TTLCache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:4000").rstrip("/")
INTROSPECTION_ENDPOINT = os.getenv("INTROSPECTION_ENDPOINT", "/connect/introspect")
AUTH_CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET = os.getenv("AUTH_CLIENT_SECRET")
REQUIRED_AUDIENCE = os.getenv("REQUIRED_AUDIENCE", "auth-template-api")
REQUIRED_SCOPES: Set[str] = set(os.getenv("REQUIRED_SCOPES", "").split())

bearer = HTTPBearer(auto_error=False)
cache: TTLCache[str, dict] = TTLCache(maxsize=1024, ttl=30)


class IntrospectionResult(BaseModel):
    active: bool
    sub: Optional[str] = None
    aud: Optional[str] = None
    scope: Optional[str] = None
    client_id: Optional[str] = None
    exp: Optional[int] = None
    role: Optional[str] = None  # NEW


async def introspect(token: str) -> IntrospectionResult:
    if not AUTH_CLIENT_ID or not AUTH_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server auth config missing: set AUTH_CLIENT_ID and AUTH_CLIENT_SECRET",
        )
    if token in cache:
        return IntrospectionResult(**cache[token])

    url = f"{AUTH_SERVER_URL}{INTROSPECTION_ENDPOINT}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(
            url,
            data={"token": token},
            auth=(AUTH_CLIENT_ID, AUTH_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Introspection failed")

    data = resp.json()
    cache[token] = data
    return IntrospectionResult(**data)


def _has_scopes(token_scopes: Optional[str], required: Set[str]) -> bool:
    if not required:
        return True
    provided = set(token_scopes.split()) if token_scopes else set()
    return required.issubset(provided)


async def require_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> IntrospectionResult:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")

    token = credentials.credentials
    result = await introspect(token)

    if not result.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive token")

    if REQUIRED_AUDIENCE and result.aud and result.aud != REQUIRED_AUDIENCE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid audience")

    if not _has_scopes(result.scope, REQUIRED_SCOPES):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient scopes")

    return result


