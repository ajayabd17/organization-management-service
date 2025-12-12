from pydantic import BaseModel

class CreateOrgRequest(BaseModel):
    organization_name: str
    email: str
    password: str

class GetOrgRequest(BaseModel):
    organization_name: str

class UpdateOrgRequest(BaseModel):
    organization_name: str  # New name
    email: str
    password: str

class DeleteOrgRequest(BaseModel):
    organization_name: str

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class OrgResponse(BaseModel):
    org_name: str
    collection_name: str
    admin_email: str