from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers import admin, org


app = FastAPI(
    title="Organization Management Service",
    description="Backend Intern Assignment – Multi-tenant Organization Management with MongoDB",
    version="1.0.0",
    openapi_tags=[
        {"name": "org", "description": "Organization CRUD operations"},
        {"name": "admin", "description": "Authentication"},
    ],
)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


app.include_router(org.router, prefix="/org", tags=["org"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])