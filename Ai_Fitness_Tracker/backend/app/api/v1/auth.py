from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from urllib.parse import urlencode
import time
import httpx
from jose import jwt, jwk
from ...schemas.schemas import UserRegister, UserLogin, UserResponse, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest, TOTPSetupResponse, TOTPVerifyRequest, ChangePasswordRequest
from ..dependencies import get_db, get_current_user
from ...services.auth_service import AuthService
from ...db.models import User
from ...core.config import settings
from ...core.security import create_access_token
from ...db.repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register_user(user)


@router.post("/signup", response_model=TokenResponse)
async def signup(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """Alias for /register endpoint for backward compatibility"""
    auth_service = AuthService(db)
    return await auth_service.register_user(user)


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(user.username, user.password)


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.forgot_password(request.email)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.reset_password(request.token, request.new_password)


@router.post("/totp/setup", response_model=TOTPSetupResponse)
async def setup_totp(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.setup_totp(current_user)


@router.post("/totp/verify")
async def verify_totp(request: TOTPVerifyRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.verify_totp(current_user, request.otp)


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.change_password_with_totp(current_user, request.new_password, request.totp_code)


def _get_base_web_url() -> str:
    return settings.WEB_BASE_URL.rstrip("/")


def _redirect_with_token(access_token: str):
    return RedirectResponse(f"{_get_base_web_url()}/?token={access_token}")


def _require_google_settings() -> None:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google OAuth is not configured")


def _require_apple_settings() -> None:
    if not settings.APPLE_CLIENT_ID or not settings.APPLE_TEAM_ID or not settings.APPLE_KEY_ID or not settings.APPLE_PRIVATE_KEY or not settings.APPLE_REDIRECT_URI:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Apple OAuth is not configured")


def _create_apple_client_secret() -> str:
    private_key = settings.APPLE_PRIVATE_KEY.replace("\\n", "\n")
    now = int(time.time())
    exp = now + int(timedelta(days=180).total_seconds())
    headers = {"kid": settings.APPLE_KEY_ID}
    claims = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": now,
        "exp": exp,
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID
    }
    return jwt.encode(claims, private_key, algorithm="ES256", headers=headers)


async def _get_or_create_oauth_user(db: AsyncSession, username: str):
    user_repo = UserRepository(db)
    return await user_repo.get_or_create_oauth_user(username)


@router.get("/google/login")
def google_login():
    _require_google_settings()
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    _require_google_settings()
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            },
            timeout=10
        )
    if token_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token exchange failed")
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google access token missing")
    
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google userinfo failed")
    userinfo = userinfo_response.json()
    email = (userinfo.get("email") or "").lower()
    subject = userinfo.get("sub")
    username = email if email else f"google_{subject}"
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account missing identifier")
    user = await _get_or_create_oauth_user(db, username)
    app_token = create_access_token({"sub": user.username})
    return _redirect_with_token(app_token)


@router.get("/apple/login")
def apple_login():
    _require_apple_settings()
    params = {
        "client_id": settings.APPLE_CLIENT_ID,
        "redirect_uri": settings.APPLE_REDIRECT_URI,
        "response_type": "code",
        "response_mode": "query",
        "scope": "name email"
    }
    url = f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/apple/callback")
async def apple_callback(code: str, db: AsyncSession = Depends(get_db)):
    _require_apple_settings()
    client_secret = _create_apple_client_secret()
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://appleid.apple.com/auth/token",
            data={
                "client_id": settings.APPLE_CLIENT_ID,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.APPLE_REDIRECT_URI
            },
            timeout=10
        )
    if token_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple token exchange failed")
    token_data = token_response.json()
    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple id_token missing")
    header = jwt.get_unverified_header(id_token)
    
    async with httpx.AsyncClient() as client:
        apple_keys_resp = await client.get("https://appleid.apple.com/auth/keys", timeout=10)
    apple_keys = apple_keys_resp.json().get("keys", [])
    
    key_data = next((k for k in apple_keys if k.get("kid") == header.get("kid")), None)
    if not key_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple key not found")
    public_key = jwk.construct(key_data).to_pem()
    claims = jwt.decode(
        id_token,
        public_key,
        algorithms=["RS256"],
        audience=settings.APPLE_CLIENT_ID,
        issuer="https://appleid.apple.com"
    )
    email = (claims.get("email") or "").lower()
    subject = claims.get("sub")
    username = email if email else f"apple_{subject}"
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple account missing identifier")
    user = await _get_or_create_oauth_user(db, username)
    app_token = create_access_token({"sub": user.username})
    return _redirect_with_token(app_token)
