from fastapi.responses import JSONResponse
from services.botresponse import BotResponse
from services.history import History

def sugar_support(data, query):
    preferences = History.getPreferences(data["id"])
    sugar_response = BotResponse.sugar_response(query, data, preferences).content
    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": sugar_response})    
    return JSONResponse(content = {"response": sugar_response, "showSubOptions": False, "showOptions": True}, status_code=200)