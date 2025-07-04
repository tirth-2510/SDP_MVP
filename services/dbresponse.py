import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

mongoClient = MongoClient(os.getenv("MONGODB_URI"))
db=mongoClient["sdp_chatbot"]
collection=db["foodItems"]
        
class mongoDB():
    def getLastConv(id: str, sec: str):
        return collection.find_one({"userId": id, "section": sec}, sort=[("timestamp", -1)])
    
    def setSumPref(userId: str, summary: str, preferences: str):
        collection.find_one_and_update(
            {"userId": userId},
            {"$set": {"summary": summary, "preferences": preferences}},
            upsert=True
        )
