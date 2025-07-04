from langchain_core.messages import HumanMessage, AIMessage
from services.prompts import Prompt
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# <----- Use this for PRODUCTION testing and in PRODUCTION. ----->
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_tokens=None, api_key=os.getenv("GOOGLE_API_KEY"))

# <----- Use this for LOCAL testing while DEVELOPING. ----->
# llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0, max_tokens=None, api_key=os.getenv("GROQ_API_KEY"))
# llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0, max_tokens=None, api_key=os.getenv("GROQ_API_KEY"))

class BotResponse:
    @staticmethod
    def summary_response(conversations: list) -> AIMessage:
        prompt = Prompt.getChatSummaryPrompt()
        conversations.append(HumanMessage(content=prompt))
        return llm.invoke(conversations)
    
    @staticmethod
    def intent_response(query: str, chat_history: list):
        prompt = Prompt.getIntentPrompt(query)
        try:
            chat_history.append(HumanMessage(content=prompt))
            chat_history.append(HumanMessage(content=query))
            return llm.invoke(chat_history)
        except Exception as e:
            return {"res": "Invalid response from model." + e}

    @staticmethod
    def collection_response(conversation: list, query: str, collected_meals: str):
        prompt = Prompt.getCollectPrompt(collected_meals)
        try:
            conversation.append(HumanMessage(content=prompt))
            conversation.append(HumanMessage(content=query))
            return llm.invoke(conversation)
        except Exception as e:
            return {"res": "Invalid response from model."+e}

    @staticmethod
    def recall_response(conversation: list, query: str, collected_meals: str):
        prompt = Prompt.getDietRecallPrompt(plan=collected_meals)
        try:
            conversation.append(HumanMessage(content=prompt))
            conversation.append(HumanMessage(content=query))
            return llm.invoke(conversation)
        except Exception as e:
            return {"res": "Invalid response from model." + e}

    @staticmethod
    def recall_analysis_response(collected_meals: str, conditions: str, calories: int = 1600):
        conversation = []
        prompt = Prompt.getDietRecallAnalysisPrompt(plan=collected_meals, conditions=conditions, calories=calories)
        try:
            conversation.append(HumanMessage(content=prompt))
            return llm.invoke(conversation)
        except Exception as e:
            return {"res": "Invalid response from model." + e}
        
    @staticmethod
    def generate_plan_response(data: dict, current_meals: str, preferences: dict, query: str):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        calorie_goal = data["calorie_goal"]
        conditions = data["conditions"]
        allergies = data["allergies"]
        messages = []
        prompt = Prompt.getDietPlan(name=name, plan=current_meals, community=community, food_type=foodPref, calorie_goal=calorie_goal, conditions=conditions, allergies=allergies, preferences=preferences)
        try:
            messages.append(HumanMessage(content=prompt))
            messages.append(HumanMessage(content=query))
            return llm.invoke(messages)
        except Exception as e:
            return {"res": "Invalid response from model." + e}

    @staticmethod
    def improve_plan_response(data: dict, collected_meals: str, preferences: dict):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        allergies = data["allergies"]
        conditions = data["conditions"]
        calories = data["calorie_goal"]
        conversation = []
        prompt = Prompt.getDietImprovements(name=name, community=community, foodType=foodPref, current_plan=collected_meals, calorie_goal=calories, conditions=conditions, preferences=preferences,allergies=allergies)
        try:
            conversation.append(HumanMessage(content=prompt))
            return llm.invoke(conversation)
        except Exception as e:
            return {"res": "Invalid response from model." + e}
    
    @staticmethod
    def advice_response(query: str, data: dict, preferences: dict):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        allergies = data["allergies"]
        conditions = data["conditions"]
        calories = data["calorie_goal"]
        prompt = Prompt.getFoodAdvicePrompt(name, conditions, allergies, preferences, foodPref, calories, community)
        messages = []
        try:
            messages.append(HumanMessage(content=prompt))
            messages.append(HumanMessage(content=query))
            return llm.invoke(messages)
        except Exception as e:
            return {"res": "Invalid response from model." + e}


# <-------------------- BUGGY PART (FLOW IS NOT DECIDED YET) -------------------->

    @staticmethod
    def food_review_response(query: str, data: dict, preferences: dict):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        allergies = data["allergies"]
        conditions = data["conditions"]
        calories = data["calorie_goal"]
        prompt = Prompt.getFoodReviewPrompt(name, conditions, allergies, preferences, foodPref, calories, community)
        messages = []
        try:
            messages.append(HumanMessage(content=prompt))
            messages.append(HumanMessage(content=query))
            return llm.invoke(messages)
        except Exception as e:
            return {"res": "Invalid response from model." + e}

    @staticmethod
    def sugar_response(query:str, data:dict, preferences:dict):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        allergies = data["allergies"]
        conditions = data["conditions"]
        calories = data["calorie_goal"]
        prompt = Prompt.getSugarAnalysisPrompt(name, conditions, allergies, preferences, foodPref, calories, community)
        messages = []
        try:
            messages.append(HumanMessage(content=prompt))
            messages.append(HumanMessage(content=query))
            return llm.invoke(messages)
        except Exception as e:
            return {"res": "Invalid response from model." + e}
    
    @staticmethod
    def lifestyle_response(query:str, data:dict, preferences:dict):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        allergies = data["allergies"]
        conditions = data["conditions"]
        calories = data["calorie_goal"]
        prompt = Prompt.getLifestylePrompt(name, conditions, allergies, preferences, foodPref, calories, community)
        messages = []
        try:
            messages.append(HumanMessage(content=prompt))
            messages.append(HumanMessage(content=query))
            return llm.invoke(messages)
        except Exception as e:
            return {"res": "Invalid response from model." + e}
    
    @staticmethod
    def medic_response(query:str, data:dict, preferences:dict):
        name = data["name"]
        community = data["community"]
        foodPref = data["food_type"]
        allergies = data["allergies"]
        conditions = data["conditions"]
        calories = data["calorie_goal"]
        prompt = Prompt.getMedicPrompt(name, conditions, allergies, preferences, foodPref, calories, community)
        messages = []
        try:
            messages.append(HumanMessage(content=prompt))
            messages.append(HumanMessage(content=query))
            return llm.invoke(messages)
        except Exception as e:
            return {"res": "Invalid response from model." + e}
    
