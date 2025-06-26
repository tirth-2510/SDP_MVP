import os
from pymongo import MongoClient

mongoClient = MongoClient(os.getenv("MONGODB_URI"))
db=mongoClient["sdp_chatbot"]
collection=db["foodItems"]

class mongoDB():    
    def getLastConv(id: str, sec: str):
        return collection.find_one({"userId": id, "section": sec}, sort=[("timestamp", -1)])