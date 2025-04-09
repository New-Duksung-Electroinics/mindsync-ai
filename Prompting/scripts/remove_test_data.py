from Prompting.repository.mongo_client import MONGO_URI, ROOM_COLLECTION, CHAT_COLLECTION, AGENDA_COLLECTION, USER_COLLECTION, MONGO_DB_NAME
from pymongo import MongoClient


client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# 테스트 기준값(버전이나 room_id)
# TEST_ROOM_ID = "TEST_ROOM_ID"
TEST_VERSION = "v1"

def remove_all():
    print("🧹 Removing test data...")

    db[ROOM_COLLECTION].delete_many({"meta.version": TEST_VERSION})
    db[AGENDA_COLLECTION].delete_many({"meta.version": TEST_VERSION})
    db[CHAT_COLLECTION].delete_many({"meta.version": TEST_VERSION})
    db[USER_COLLECTION].delete_many({"meta.version": TEST_VERSION})

    print("✅ Done removing test data.")

if __name__ == "__main__":
    remove_all()
