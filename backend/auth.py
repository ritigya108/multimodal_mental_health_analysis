"""
auth.py — Lightweight JWT authentication helpers.

Uses python-jose for token generation/verification and passlib for password
hashing.  The SECRET_KEY MUST be overridden via the JWT_SECRET_KEY environment
variable before deploying to production.

Usage
-----
  from auth import get_current_user, create_access_token, router as auth_router

  # In main.py:
  app.include_router(auth_router)

  # On protected endpoints:
  @app.get("/api/protected")
  async def protected(user: dict = Depends(get_current_user)):
      return {"user_id": user["sub"]}
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_SECRET_KEY: str = os.environ.get(
    "JWT_SECRET_KEY",
    "CHANGE_ME_BEFORE_DEPLOYMENT_use_a_long_random_secret",
)
_ALGORITHM    = "HS256"
_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", "72"))

# Optional: set to True to make all endpoints require a valid JWT.
# False (default) keeps the API open while JWT is in development.
_AUTH_REQUIRED: bool = os.environ.get("JWT_AUTH_REQUIRED", "false").lower() == "true"

_bearer = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def create_access_token(payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Return a signed JWT string.  `payload` must contain a 'sub' (subject) key."""
    try:
        from jose import jwt as _jwt
    except ImportError as e:
        raise RuntimeError("python-jose is not installed. Run: pip install python-jose[cryptography]") from e

    data = payload.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=_EXPIRE_HOURS))
    data["exp"] = expire
    return _jwt.encode(data, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT.  Raises HTTPException 401 on failure."""
    try:
        from jose import jwt as _jwt, JWTError
    except ImportError as e:
        raise RuntimeError("python-jose is not installed. Run: pip install python-jose[cryptography]") from e

    try:
        payload = _jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        if "sub" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Dict[str, Any]:
    """
    FastAPI dependency — resolves to the decoded JWT payload dict.

    Behaviour:
    - If JWT_AUTH_REQUIRED=true and no/invalid token  → 401
    - If JWT_AUTH_REQUIRED=false and no token         → returns anonymous user dict
    - If JWT_AUTH_REQUIRED=false and invalid token    → 401 (prevents accidental use of bad tokens)
    """
    if credentials is None:
        if _AUTH_REQUIRED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Anonymous guest user — used during development
        return {"sub": "anonymous", "name": "Guest", "role": "user"}

    return decode_token(credentials.credentials)


def get_user_id(user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """Shortcut dependency — resolves directly to the user's string ID."""
    return user.get("sub", "anonymous")


# ---------------------------------------------------------------------------
# Auth router  (POST /auth/token)
# ---------------------------------------------------------------------------
# This is a *demo* login endpoint: any non-empty username + password is
# accepted and a JWT is issued.  Replace the body of `_login` with your
# real user-store lookup before going to production.

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: str


@router.post("/token", response_model=TokenResponse, summary="Issue a JWT access token")
async def login(req: LoginRequest) -> TokenResponse:
    """
    Demo authentication endpoint.

    Accepts any non-empty username + password and returns a signed JWT.
    Replace the stub below with a real database lookup before production.
    """
    if not req.username.strip() or not req.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username and password are required.",
        )

    # ── TODO: replace with real DB lookup + bcrypt verify ──────────────────
    # Example real check:
    #   user = await db.get_user_by_username(req.username)
    #   if not user or not verify_password(req.password, user.hashed_password):
    #       raise HTTPException(401, "Invalid credentials")
    # ───────────────────────────────────────────────────────────────────────
    user_id = req.username.lower().replace(" ", "_")

    token = create_access_token({"sub": user_id, "name": req.username})
    expires = int(timedelta(hours=_EXPIRE_HOURS).total_seconds())
    return TokenResponse(access_token=token, expires_in_seconds=expires, user_id=user_id)
