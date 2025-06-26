import os
import redis
import json
from collections import deque
from dbresponse import mongoDB

# PRODUCTION
r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), ssl=True, db=0)

# LOCAL TESTING
# r = redis.Redis(host="localhost", port=6379, db=0)

class History:
    @staticmethod
    def getHistory(userId: str, section: str) -> dict | None:
        # Check if user exists (12 hours up?)
        existUser = mongoDB.getLastConv(id=userId, sec=section)
        
        # Maybe user exists and history is stored in mongo
        if existUser:
            r.hset(userId, mapping={section: json.dumps(existUser)})
            if r.ttl(userId) == -1:
                r.expire(userId, 43200) # 12 hours
            return json.loads(existUser)
        
        # Its a complete new user or Conversation is stored in redis 12hrs not up yet for first user.
        response = r.hget(userId, section)
        return(json.loads(response) if response else None)
    
    @staticmethod
    def setHistory(userId: str, section:str, newConversation: dict):
        
        response = History.getHistory(userId, section)
        
        # Conversation exists
        if response:
            conversationArray = deque(maxlen=10)
            for conv in response.values():
                conversationArray.append(json.loads(conv))
            conversationArray.append(newConversation)
            updatedConversationMemory = {str(i) : json.dumps(conv) for i, conv in enumerate(conversationArray)}
            r.hset(userId, mapping={section: json.dumps(updatedConversationMemory)})

        # Its the first question
        else:
            
            # Check if user exists (12 hours up?)
            existUser = mongoDB.getLastConv(id=userId, sec=section)
        
            if existUser:
                r.hset(userId, mapping={section: json.dumps(existUser)})
                if r.ttl(userId) == -1:
                    r.expire(userId, 43200) # 12 hours
                    
            # New User
            else:
                r.hset(userId, mapping={section: json.dumps({"0": json.dumps(newConversation)})})
                if r.ttl(userId) == -1:
                    r.expire(userId, 43200) # 12 hours

    @staticmethod
    def appendMealSlot(userId: str, new_meals: dict):
        meals = History.getUserMeals(userId) or {}
        for slot in new_meals:
            meals[slot] = new_meals[slot]
        r.hset(userId, "meals", json.dumps(meals))

    @staticmethod
    def getUserMeals(userId: str) -> dict:
        data = r.hget(userId, "meals")
        return json.loads(data) if data else None
    
    @staticmethod
    def getChatState(userId: str) -> str:
        return r.hget(userId, "chat_state") or "collect"
    
    @staticmethod
    def setChatState(userId: str, state: str):
        r.hset(userId, "chat_state", state)
 