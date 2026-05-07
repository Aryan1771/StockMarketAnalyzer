from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import MONGODB_DB_NAME, MONGODB_URI


class DbService:
    def __init__(self):
        self.client = None
        self.db = None
        self.enabled = False

        if not MONGODB_URI:
            return

        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client[MONGODB_DB_NAME]
            self.enabled = True
            self._ensure_indexes()
        except PyMongoError:
            self.client = None
            self.db = None
            self.enabled = False

    def _ensure_indexes(self):
        users = self.db["users"]
        users.create_index("username", unique=True, sparse=True)
        users.create_index([("authProvider", 1), ("providerUserId", 1)], unique=True, sparse=True)
        users.create_index("email", sparse=True)

    def users(self):
        if not self.enabled:
            raise RuntimeError("MongoDB is not configured")
        return self.db["users"]


db_service = DbService()
