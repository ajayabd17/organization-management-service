from fastapi import APIRouter, HTTPException

from app.auth import Auth
from app.database import Database
from app.models import AdminLoginRequest

router = APIRouter()

db = Database()

@router.post("/login")
def admin_login(request: AdminLoginRequest):
    metadata = db.get_org_by_admin(request.email)
    if not metadata or not db.check_password(request.password, metadata["admin_password"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = Auth.create_access_token(metadata["admin_email"], metadata["org_name"])  # Use email as admin_id, org_name as org_id
    return {"access_token": token, "token_type": "bearer"}