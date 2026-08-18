"""
OAuth2 handlers: Google, GitHub, Telegram.
Each handler:
  1. Redirects user to provider
  2. Receives callback, fetches user info
  3. Returns JWT token
"""
import hashlib, hmac, time
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig
from starlette.requests import Request
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from .jwt import create_token
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
from mas.config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
    TELEGRAM_BOT_TOKEN,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

_starlette_cfg = StarletteConfig(environ={
    "GOOGLE_CLIENT_ID":     GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
    "GITHUB_CLIENT_ID":     GITHUB_CLIENT_ID,
    "GITHUB_CLIENT_SECRET": GITHUB_CLIENT_SECRET,
})

oauth = OAuth(_starlette_cfg)

if GOOGLE_CLIENT_ID:
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if GITHUB_CLIENT_ID:
    oauth.register(
        name="github",
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )


# ── Google ──────────────────────────────────────────────────────────

@router.get("/google/login")
async def google_login(request: Request):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(400, "Google OAuth not configured")
    redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo") or {}
    jwt_token = create_token({
        "sub": user_info.get("sub", ""),
        "email": user_info.get("email", ""),
        "name": user_info.get("name", ""),
        "provider": "google",
    })
    return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})


# ── GitHub ──────────────────────────────────────────────────────────

@router.get("/github/login")
async def github_login(request: Request):
    if not GITHUB_CLIENT_ID:
        raise HTTPException(400, "GitHub OAuth not configured")
    redirect_uri = str(request.url_for("github_callback"))
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback", name="github_callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    profile = resp.json()
    jwt_token = create_token({
        "sub": str(profile.get("id", "")),
        "email": profile.get("email", ""),
        "name": profile.get("login", ""),
        "provider": "github",
    })
    return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})


# ── Telegram Login Widget ────────────────────────────────────────────

@router.get("/telegram/callback")
async def telegram_callback(
    id: int, first_name: str = "", username: str = "",
    hash: str = "", auth_date: int = 0, **_kwargs
):
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(400, "Telegram auth not configured")

    # Verify hash — Telegram spec
    bot_secret = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    data_string = "\n".join(
        f"{k}={v}" for k, v in sorted({
            "id": id, "first_name": first_name,
            "username": username, "auth_date": auth_date,
        }.items()) if v
    )
    expected = hmac.new(bot_secret, data_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, hash):
        raise HTTPException(401, "Telegram auth signature invalid")
    if time.time() - auth_date > 86400:
        raise HTTPException(401, "Telegram auth token expired")

    jwt_token = create_token({
        "sub": str(id),
        "name": first_name or username,
        "provider": "telegram",
    })
    return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})


# ── Token info ───────────────────────────────────────────────────────

@router.get("/me")
async def me(request: Request):
    from .jwt import current_user, oauth2_scheme
    from fastapi import Depends
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    from .jwt import decode_token
    return decode_token(auth[7:])
