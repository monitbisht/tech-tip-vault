from pymongo import MongoClient, ASCENDING
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
tips_collection = db["tips"]

def setup_indexes():
    """
    Creates a multikey index on the 'tags' array field.
    MongoDB automatically creates a multikey index when the field contains an array.
    """
    tips_collection.create_index([("tags", ASCENDING)])
    tips_collection.create_index([("type", ASCENDING)])
    tips_collection.create_index([("subcategory", ASCENDING)])
    print("MongoDB indexes created successfully.")
