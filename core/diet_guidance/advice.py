from services.botresponse import BotResponse
from fastapi import Response
from services.history import History

def food_advice(query, data):
    preferences = History.getPreferences(data["id"])
    advice_response = BotResponse.advice_response(query, data, preferences).content
    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": advice_response})
    return Response(content={"response": advice_response, "showSubOptions": False, "showOptions": True}, status_code=200)
