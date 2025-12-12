"""Mongo-backed data access layer for organization metadata and dynamic collections."""

import os
from typing import Any, Dict, Optional

import bcrypt
from pymongo import MongoClient
from pymongo.collection import Collection


class Database:
    """Singleton wrapper around MongoDB operations."""

    _instance: Optional["Database"] = None

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self) -> None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "org_service")
        self.client = MongoClient(uri)
        self.master_db = self.client[db_name]
        self.org_collection: Collection = self.master_db["organizations"]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.org_collection.create_index("org_name", unique=True)
        self.org_collection.create_index("admin_email", unique=True)

    # Password helpers
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, candidate: str, hashed: str) -> bool:
        return bcrypt.checkpw(candidate.encode(), hashed.encode())

    # Metadata operations
    def create_org_metadata(self, org_name: str, email: str, hashed_password: str, collection_name: str) -> Dict[str, Any]:
        doc = {
            "org_name": org_name,
            "collection_name": collection_name,
            "admin_email": email,
            "admin_password": hashed_password,
        }
        self.org_collection.insert_one(doc)
        return doc

    def get_org_metadata(self, org_name: str) -> Optional[Dict[str, Any]]:
        return self.org_collection.find_one({"org_name": org_name})

    def get_org_by_admin(self, admin_email: str) -> Optional[Dict[str, Any]]:
        return self.org_collection.find_one({"admin_email": admin_email})

    def update_org_metadata(self, old_org_name: str, new_org_name: str, new_email: str, new_hashed_password: str) -> str:
        new_collection_name = f"org_{new_org_name}"
        self.org_collection.find_one_and_update(
            {"org_name": old_org_name},
            {
                "$set": {
                    "org_name": new_org_name,
                    "collection_name": new_collection_name,
                    "admin_email": new_email,
                    "admin_password": new_hashed_password,
                }
            },
        )
        return new_collection_name

    def delete_org_metadata(self, org_name: str) -> None:
        self.org_collection.delete_one({"org_name": org_name})

    # Dynamic collection operations
    def create_dynamic_collection(self, collection_name: str) -> Collection:
        return self.master_db[collection_name]

    def drop_dynamic_collection(self, collection_name: str) -> None:
        self.master_db.drop_collection(collection_name)

    def sync_data_to_new_collection(self, old_collection_name: str, new_collection_name: str) -> None:
        if old_collection_name == new_collection_name:
            return

        old_coll = self.master_db[old_collection_name]
        new_coll = self.master_db[new_collection_name]

        documents = list(old_coll.find())
        if documents:
            for doc in documents:
                doc.pop("_id", None)
            new_coll.insert_many(documents)

        self.drop_dynamic_collection(old_collection_name)
