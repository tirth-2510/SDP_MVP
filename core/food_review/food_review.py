from fastapi.responses import JSONResponse
from services.history import History
from services.botresponse import BotResponse

def food(data, query):
    preferences = History.getPreferences(data["id"])
    review_response = BotResponse.food_review_response(query, data, preferences).content
    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": review_response})
    return JSONResponse(content = {"response": review_response, "showSubOptions": False, "showOptions": True}, status_code=200)