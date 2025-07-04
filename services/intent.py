from services.botresponse import BotResponse
from services.conversations import getLastChats
import json
def getIntent(userId: str, query: str) -> str:

    # FAILED
    # intent_keywords = {
    #     "meal_advice": [
    #         "what should i eat", "meal advice", "breakfast idea", "lunch idea", "dinner idea", "snack idea",
    #         "suggest me something to eat", "meal suggestion", "food suggestion", "need meal", "meal tip",
    #         "recommend meal", "i need help with lunch", "what to eat", "eating today", "can i eat", "food option",
    #         "help me with breakfast", "any food tip", "recommend food", "today's menu", "i feel hungry",
    #         "need food", "food options for now", "share some meal advice"
    #     ],
    #     "diet_plan_today": [
    #         "today's diet", "diet for today", "what to eat today", "today meal plan", "diet suggestion for today",
    #         "today diet chart", "today's meals", "daily diet plan", "today food plan", "today’s nutrition plan",
    #         "today diet recommendation", "share today plan", "give diet for today", "plan my diet today"
    #     ],
    #     "diet_plan_week": [
    #         "weekly plan", "weekly diet", "diet for the week", "meal plan for week", "7 day diet plan",
    #         "full week plan", "plan for whole week", "weekly food guide", "next 7 days plan",
    #         "can you plan my week", "plan meals for this week", "week long meal plan"
    #     ],
    #     "analyze_diet_today": [
    #         "analyze my diet", "check my meals", "how was my diet", "what did i eat today", "review my meals",
    #         "track what i ate", "evaluate today diet", "was my diet okay", "see what i ate", "recall today's diet",
    #         "analyze today's meals", "did i eat healthy", "give feedback on my diet", "analyze what i ate today"
    #     ],
    #     "improve_current_diet": [
    #         "how can i improve", "improve my diet", "what should i change", "what to avoid", "how to make better",
    #         "diet correction", "fix my meals", "optimize diet", "suggest improvement", "improve eating habit",
    #         "make my diet better", "help me improve diet", "what to change in my food", "how to enhance nutrition"
    #     ],
    # }

    # user_text_clean = re.sub(r'[^\w\s]', '', query)
    # for intent, keywords in intent_keywords.items():
    #     for phrase in keywords:
    #         if phrase in user_text_clean:
    #             return {"intent": intent, "use_gemini": False}
    # return {"intent": "unknown", "use_gemini": True}
    chats = getLastChats(user_id=userId)
    response = BotResponse.intent_response(query, chats).content
    return json.loads(response) if response else None