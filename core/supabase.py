"""
Supabase client singleton and auth edge-function client.

Supabase SDK handles:
  - JWT verification (via supabase.auth.get_user(token))
  - Token refresh
  - All other RPC / storage / realtime concerns

This module exposes:
  - `get_client()` – returns the async Supabase client
  - `internal_auth(payload)` – POSTs to the internal-auth edge function and
    parses the response with the models from models.auth, returning either
    AuthSuccess or AuthError as the discriminated union.
"""

import httpx
from supabase import AsyncClient, acreate_client
from urllib.parse import urljoin

from config import config
from models.auth import AuthRequest, AuthResponse, auth_response_adapter

__all__ = ["get_client", "internal_auth"]

# Internal-auth edge function endpoint (fixed, per task spec)
_INTERNAL_AUTH_URL = urljoin(config.SUPABASE_URL, "/functions/v1/internal-auth")


# Async Supabase client (lazy singleton)
_supabase_client: AsyncClient | None = None


async def get_client() -> AsyncClient:
    """Return a cached async Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = await acreate_client(
            config.SUPABASE_URL,
            config.SUPABASE_ANON_KEY,
        )
    return _supabase_client


# Edge-function caller
async def internal_auth(payload: AuthRequest) -> AuthResponse:
    """
    POST the serialised AuthRequest (register or login) to the internal-auth
    edge function and return the parsed AuthSuccess | AuthError union.

    Serialisation/deserialisation uses the models defined in models.auth so
    the shapes always match what the function expects and what it returns.
    """
    body = payload.model_dump(mode="json")

    async with httpx.AsyncClient(timeout=15.0) as http:
        response = await http.post(
            _INTERNAL_AUTH_URL,
            json=body,
            headers={
                "Content-Type": "application/json",
                # The Supabase anon key authorises the edge-function invocation.
                "Authorization": f"Bearer {config.SUPABASE_ANON_KEY}",
                "apikey": config.SUPABASE_ANON_KEY,
            },
        )

    # The function may return a non-2xx status together with an AuthError body.
    # We parse the body regardless of status (AuthSuccess | AuthError union).
    return auth_response_adapter.validate_python(response.json())
