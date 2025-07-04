from fastapi.responses import JSONResponse
from services.history import History
from services.botresponse import BotResponse

def lifestyle(data, query):
    preferences = History.getPreferences(data["id"])
    lifestyle_response = BotResponse.lifestyle_response(query, data, preferences).content
    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": lifestyle_response})
    return JSONResponse(content = {"response": lifestyle_response, "showSubOptions": False, "showOptions": True}, status_code=200)