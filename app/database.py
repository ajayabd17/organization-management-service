from pymongo import MongoClient
import bcrypt

class Database:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["master_db"]  # Master database
        self.org_collection = self.db["organizations"]  # Collection for metadata

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def create_org_metadata(self, org_name: str, admin_email: str, hashed_password: str, collection_name: str):
        metadata = {
            "org_name": org_name,
            "collection_name": collection_name,
            "admin_email": admin_email,
            "admin_password": hashed_password  # Stored hashed
        }
        self.org_collection.insert_one(metadata)
        return metadata

    def get_org_metadata(self, org_name: str):
        return self.org_collection.find_one({"org_name": org_name})

    def update_org_metadata(self, old_org_name: str, new_org_name: str, new_email: str, new_hashed_password: str):
        new_collection_name = f"org_{new_org_name}"
        # Update metadata
        self.org_collection.update_one(
            {"org_name": old_org_name},
            {"$set": {"org_name": new_org_name, "collection_name": new_collection_name, "admin_email": new_email, "admin_password": new_hashed_password}}
        )
        return new_collection_name

    def delete_org_metadata(self, org_name: str):
        self.org_collection.delete_one({"org_name": org_name})

    def create_dynamic_collection(self, collection_name: str):
        # Creates if not exists; MongoDB collections are created on first insert, but we can touch it
        self.db[collection_name].insert_one({"init": True})  # Optional init
        self.db[collection_name].delete_one({"init": True})  # Clean up

    def drop_dynamic_collection(self, collection_name: str):
        self.db[collection_name].drop()

    def sync_data_to_new_collection(self, old_collection_name: str, new_collection_name: str):
        old_coll = self.db[old_collection_name]
        new_coll = self.db[new_collection_name]
        for doc in old_coll.find():
            new_coll.insert_one(doc)
        old_coll.drop()  # Drop old after sync