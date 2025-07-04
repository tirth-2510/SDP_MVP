import redis
import json
from collections import deque
from services.dbresponse import mongoDB
from services.botresponse import BotResponse
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

# PRODUCTION
r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), ssl=True, db=0)

# LOCAL TESTING
# r = redis.Redis(host="localhost", port=6379, db=0)

class History:

    # <---------- HISTORY ---------->

    # HISTORY
    @staticmethod
    def getHistory(userId: str, section: str = "chats") -> dict | None:
        '''Get a specific section of the user session history.
        Returns:
            {'0': '{"user": "hello", "assistant": "world"}', '1': '{"user": "marco", "assistant": "polo"}', '2': '{"user": "zip", "assistant": "zap"}'}
        '''
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
    def setHistory(userId: str, newConversation: dict, section: str = "chats"):
        # Load existing history
        response = History.getHistory(userId, section)

        # Create a conversation deque
        conversationArray = deque(maxlen=10)

        # If conversations exist
        if response:
            for conv in response.values():
                conversationArray.append(json.loads(conv))
        else:
            # Check Mongo fallback if applicable (for completeness)
            existUser = mongoDB.getLastConv(id=userId, sec=section)
            if existUser:
                for conv in existUser.values():
                    conversationArray.append(json.loads(conv))
            else:
                # Brand new user
                conversationArray.append(newConversation)
                r.hset(userId, mapping={section: json.dumps({"0": json.dumps(newConversation)}), "new_conv": "1"})
                if r.ttl(userId) == -1:
                    r.expire(userId, 43200)
                return

        # Append new conversation
        conversationArray.append(newConversation)

        # Fetch and update the conversation flag
        flag = History.getNewConvFlag(userId)
        flag = int(flag) if flag else 0
        flag += 1

        # Generate summary if 5 new conversations added
        if flag >= 5 and len(conversationArray) == 10:
            chat_to_summarize = list(conversationArray)[:5]
            conversations = []
            for conv in chat_to_summarize:
                conversations += [HumanMessage(content=conv["user"]), AIMessage(content=conv["assistant"])]

            # Call summarization logic (LLM or otherwise)
            summary = BotResponse.summary_response(conversations).content  # Should return plain string
            History.setSummary(userId, summary)

            # Reset the flag to 1 after appending new conversation
            flag = 1

        # Convert back to dict
        updatedConversationMemory = {
            str(i): json.dumps(conv) for i, conv in enumerate(conversationArray)
        }

        # Update redis
        r.hset(userId, mapping={section: json.dumps(updatedConversationMemory), "new_conv": str(flag)})
        if r.ttl(userId) == -1:
            r.expire(userId, 43200)

    # <---------- SUMMARY ---------->

    # SUMMARY
    @staticmethod
    def getSummary(userId: str):
        response = r.hget(userId, "chat_summary")
        return response.decode("utf-8") if response else None

    @staticmethod
    def setSummary(userId: str, summary: str):
        r.hset(userId, "chat_summary",summary)

    # <---------- CONVERSATION FLAGS ---------->

    # CONVERSATION FLAGS
    @staticmethod
    def getNewConvFlag(userId: str) -> int:
        response = r.hget(userId, "new_conv")
        return int(response) if response else 0

    @staticmethod
    def setNewConvFlag(userId: str, value: int):
        current = History.getNewConvFlag(userId)
        r.hset(userId, mapping={"new_conv": str(current + value)})

    @staticmethod
    def resetConvFlag(userId: str):
        r.hset(userId, mapping={"new_conv": "0"})
    
    # <---------- PREFERENCES ---------->

    # PREFERENCES
    @staticmethod
    def getPreferences(userId: str) -> dict | None:
        '''Get the user preferences.

        Args:
            userId (str): User Id.

        Returns:
            dict or None: User preferences if exists, else None.
        '''
        response = r.hget(userId, "preferences")
        return json.loads(response) if response else None
    
    @staticmethod
    def setPreferences(userId: str, preferences: dict):
        '''Set the user preferences.
        Args:
            userId (str): User Id.
            preferences (dict): User preferences to set.
        '''
        existingPreferences = History.getPreferences(userId)
        if existingPreferences:
            likesSet = set(existingPreferences["likes"])
            newPrefs = set(preferences["likes"])
            preferences = {"likes": list(likesSet.union(newPrefs))}
        r.hset(userId, mapping={"preferences": json.dumps(preferences)})
        if r.ttl(userId) == -1:
            r.expire(userId, 43200)

    # <-------- CHAT STATE ---------->

    # CHAT STATE
    @staticmethod
    def getChatState(userId: str) -> str | None:
        result = r.hget(userId, "chat_state")
        return result.decode("utf-8") if result else None
    
    @staticmethod
    def setChatState(userId: str, state: str):
        r.hset(userId, "chat_state", state)
    
    @staticmethod
    def deleteChatState(userId: str):
        r.hdel(userId, "chat_state")

    # <---------- PAST STATE ---------->

    # PAST CHAT STATE
    @staticmethod
    def getPastChatState(userId: str) -> str | None:
        result = r.hget(userId, "past_state")
        return result.decode("utf-8") if result else None
    
    @staticmethod
    def setPastChatState(userId: str, state: str):
        r.hset(userId, "past_state", state)
    
    @staticmethod
    def deletePastChatState(userId: str):
        r.hdel(userId, "past_state")

    # <---------- DIET PLANS ---------->
   
    # DIET PLAN
    @staticmethod
    def getDietPlan(userId: str):
        data = r.hget(userId, "diet_plan")
        return json.loads(data) if data else None
    
    @staticmethod
    def setDietPlan(userId: str, plan: str):
        r.hset(userId, "diet_plan", plan)

    @staticmethod
    def appendMealSlot(userId: str, new_meals: dict):
        meals = History.getDietPlan(userId) or {}
        for slot in new_meals:
            meals[slot] = new_meals[slot]
        r.hset(userId, "diet_plan", json.dumps(meals))

    # <---------- DIET RECALL ANALYSIS ---------->

    # DIET RECALL ANALYSIS
    @staticmethod
    def getDietRecallAnalysis(userId: str) -> str:
        recallAnalysis = r.hget(userId, "diet_recall_analysis")
        return recallAnalysis.decode("utf-8") if recallAnalysis else None
    
    @staticmethod
    def setDietRecallAnalysis(userId: str, analysis: str):
        r.hset(userId, "diet_recall_analysis", analysis)

    # <---------- DIET GENERATION ---------->

    # DIET GENERATION
    @staticmethod
    def getDietGeneration(userId: str) -> str:
        generation = r.hget(userId, "diet_generation")
        return generation.decode("utf-8") if generation else None
    
    @staticmethod
    def setDietGeneration(userId: str, generation: str):
        r.hset(userId, "diet_generation", generation)

    # <---------- DIET IMPROVEMENT ---------->

    # DIET IMPROVEMENT
    @staticmethod
    def getDietImprovement(userId: str) -> str:
        improvement = r.hget(userId, "diet_improvement")
        return improvement.decode("utf-8") if improvement else None
    
    @staticmethod
    def setDietImprovement(userId: str, improvement: str):
        r.hset(userId, "diet_improvement", improvement)

    # <---------- INTENT ---------->

    # INTENT
    @staticmethod
    def getIntent(userId: str) -> str:
        intent = r.hget(userId, "intent")
        return intent.decode("utf-8") if intent else None
    
    @staticmethod
    def setIntent(userId: str, intent: str):
        r.hset(userId, "intent", intent)
    
    @staticmethod
    def deleteIntent(userId: str):
        r.hdel(userId, "intent")