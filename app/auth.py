"""JWT helpers and FastAPI dependency for admin authentication."""

from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

SECRET_KEY = "super-secret-jwt-key-change-in-production-123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours for testing

http_bearer = HTTPBearer()


class Auth:
    @staticmethod
    def create_access_token(admin_email: str, org_name: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"admin_id": admin_email, "org_id": org_name, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Dict[str, str]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            admin_email = payload.get("admin_id")
            org_name = payload.get("org_id")
            if not admin_email or not org_name:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            return {"admin_email": admin_email, "org_name": org_name}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token format")


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(http_bearer)) -> Dict[str, str]:
    token = credentials.credentials
    claims = Auth.decode_token(token)

    from app.database import Database

    db = Database()
    org = db.get_org_metadata(claims["org_name"])
    if not org:
        raise HTTPException(status_code=401, detail="Organization not found")
    if org["admin_email"] != claims["admin_email"]:
        raise HTTPException(status_code=401, detail="Email mismatch")

    return claims