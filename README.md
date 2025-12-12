# Organization Management Service

FastAPI + MongoDB backend for multi-tenant organization management. The master database stores organization metadata and admin credentials; each organization gets its own dynamic collection for tenant data.

## Prerequisites
- Python 3.11+
- Running MongoDB instance (local default: `mongodb://localhost:27017`)
- Optional: virtualenv (recommended)

## Quickstart
1) Install deps:
```
pip install -r requirements.txt
```
2) Export environment (adjust as needed):
```
set MONGODB_URI=mongodb://localhost:27017
set MONGODB_DB=org_service
set SECRET_KEY=change-me
```
3) Run the API:
```
uvicorn app.main:app --reload
```
4) Open Swagger UI at http://127.0.0.1:8000/docs and click Authorize to paste the bearer token returned by `/admin/login`.

## API surface
- POST `/org/create` – create org + admin; body: `organization_name`, `email`, `password`
- GET `/org/get?organization_name=` – fetch metadata
- PUT `/org/update` – update org/admin (JWT required)
- DELETE `/org/delete` – delete org (JWT required)
- POST `/admin/login` – admin login → JWT `{access_token, token_type}`

## Design notes
- Master collection `organizations` keeps `{org_name, collection_name, admin_email, admin_password}`. Indexes enforce uniqueness on `org_name` and `admin_email`.
- Per-org data lives in dynamic collections named `org_<organization_name>`. Rename flows create a new collection, copy data, then drop the old one.
- Passwords hashed with bcrypt; JWT carries `admin_id` + `org_id`. `OAuth2PasswordBearer` powers the Swagger Authorize button.
- Configurable via env vars `MONGODB_URI` and `MONGODB_DB`. SECRET_KEY is in code for demo; set `SECRET_KEY` env in production.

### High-level Architecture Diagram
![Architecture Diagram](./architecture-diagram.png)

## Trade-offs & scalability
- Single Mongo database with per-org collections keeps onboarding lightweight; Mongo handles many collections but very high tenant counts may stress namespace management.
- JWT-only auth is simple; adding refresh tokens or revocation lists would help enterprise needs.
- Using one database keeps deployment simple; sharding per-org or per-tenant databases would isolate noisy neighbors better at the cost of operational overhead.
- Application logic is thin; a message queue could back heavy data migrations when renaming orgs instead of synchronous copy.


### Brief notes explaining the design choices

- Used **FastAPI** because it’s simple, fast to develop with, and gives interactive Swagger UI (/docs) for easy testing.
- Kept all MongoDB operations inside a single **Database** class for cleaner and more organized code.
- Used **bcrypt** to securely hash passwords and **PyJWT** for token generation.
- Implemented proper JWT authentication with **OAuth2PasswordBearer** so the green "Authorize" button appears and works smoothly in Swagger UI.
- Created dynamic MongoDB collections exactly as requested (org_<name>) and handled data sync when updating organization name.
- Protected update and delete endpoints — only the owner (authenticated admin) can modify or delete their organization.
- Made small, regular commits to show progress clearly.
- Added a simple debug endpoint to list all organizations (helpful during development).
**UUID idea in architecture note** → Mentioned in the architecture section as a small improvement I’d use in real production.

Everything follows the assignment requirements.  
Code is modular and easy to extend if needed.

Time spent: around 5 hours