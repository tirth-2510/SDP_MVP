from services.botresponse import BotResponse
from services.history import History

def sugar_support(data, query):
    preferences = History.getPreferences(data["id"])
    advice_response = BotResponse.sugar_response(query, data, preferences).content
    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": advice_response})    
    return advice_response