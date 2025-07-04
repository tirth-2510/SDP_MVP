from fastapi.responses import JSONResponse
from services.history import History
from services.botresponse import BotResponse

def medicine(data, query):
    preferences = History.getPreferences(data["id"])
    medicine_response = BotResponse.medic_response(query, data, preferences).content
    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": medicine_response})
    return JSONResponse(content = {"response": medicine_response, "showSubOptions": False, "showOptions": True}, status_code=200)