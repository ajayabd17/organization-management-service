import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your_secret_key"  # Change this to a secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Auth:
    @staticmethod
    def create_access_token(admin_id: str, org_id: str):
        to_encode = {
            "admin_id": admin_id,
            "org_id": org_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])