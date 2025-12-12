from fastapi import APIRouter, Depends, HTTPException, Query, Security

from app.auth import get_current_user
from app.database import Database
from app.models import CreateOrgRequest, DeleteOrgRequest, OrgResponse, UpdateOrgRequest

router = APIRouter()

db = Database()  # Singleton instance

@router.post("/create")
def create_org(request: CreateOrgRequest):
    if db.get_org_metadata(request.organization_name):
        raise HTTPException(status_code=400, detail="Organization already exists")
    if db.get_org_by_admin(request.email):
        raise HTTPException(status_code=400, detail="Admin email already registered")
    
    collection_name = f"org_{request.organization_name}"
    hashed_password = db.hash_password(request.password)
    
    # Create dynamic collection
    db.create_dynamic_collection(collection_name)
    
    # Create metadata (admin user is referenced via email/password in metadata)
    metadata = db.create_org_metadata(request.organization_name, request.email, hashed_password, collection_name)
    
    return OrgResponse(**{k: v for k, v in metadata.items() if k != "admin_password" and k != "_id"})

@router.get("/get")
def get_org(organization_name: str = Query(..., description="Organization name")):
    metadata = db.get_org_metadata(organization_name)
    if not metadata:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrgResponse(**{k: v for k, v in metadata.items() if k != "admin_password" and k != "_id"})

@router.put("/update")
def update_org(request: UpdateOrgRequest, current_user: dict = Security(get_current_user)):
    old_metadata = db.get_org_metadata(current_user["org_name"])
    if not old_metadata:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if db.get_org_metadata(request.organization_name) and request.organization_name != old_metadata["org_name"]:
        raise HTTPException(status_code=400, detail="New organization name already exists")
    if db.get_org_by_admin(request.email) and request.email != old_metadata["admin_email"]:
        raise HTTPException(status_code=400, detail="Admin email already registered")
    
    new_hashed_password = db.hash_password(request.password)
    new_collection_name = db.update_org_metadata(old_metadata["org_name"], request.organization_name, request.email, new_hashed_password)
    
    # Sync data to new collection
    db.sync_data_to_new_collection(old_metadata["collection_name"], new_collection_name)
    
    return {"message": "Organization updated successfully"}

@router.delete("/delete")
def delete_org(request: DeleteOrgRequest, current_user: dict = Security(get_current_user)):
    metadata = db.get_org_metadata(request.organization_name)
    if not metadata or metadata["org_name"] != current_user["org_name"]:
        raise HTTPException(status_code=403, detail="Forbidden: Can only delete own organization")
    
    # Drop dynamic collection
    db.drop_dynamic_collection(metadata["collection_name"])
    
    # Delete metadata
    db.delete_org_metadata(request.organization_name)
    
    return {"message": "Organization deleted successfully"}