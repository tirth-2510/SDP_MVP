from fastapi import Body, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import json
from langchain_core.messages import HumanMessage, AIMessage
from botresponse import BotResponse
from helper import Helper
from history import History

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# <--------- Meal Collection Logic --------->
def collect_meals(user_id: str, user_query: str, conversations: list):
    collected_meals = History.getUserMeals(user_id)
    avail_meals = Helper.textualizeMeals(collected_meals) if collected_meals else "No meals collected yet."
    airesponse = BotResponse.meal_response(conversation=conversations, query=user_query, collected_meals=avail_meals).content
    res = json.loads(airesponse)
    response = res["res"]
    if "meal" in res:
        History.appendMealSlot(user_id, res["meal"])
    if res.get("flag", False):
        History.setChatState(user_id, "confirm")
        confirm_meals = Helper.textualizeMeals(collected_meals)
        response = response + f""" Here's a quick summary of your day's meals:\n\n{confirm_meals}\n\nPlease reply YES if this is accurate, or let me know what needs to be corrected.\n"""
    History.setHistory(userId=user_id, section="meal_chats", newConversation={
        "user": user_query,
        "assistant": response
    })
    return Response(content=response, media_type="text/plain", status_code=200)

# <--------- Meal Confirmation Logic --------->
def confirm_meals(user_id: str, user_query: str, conversations: list):
    currentMeals = History.getUserMeals(user_id)
    avail_meals = Helper.textualizeMeals(currentMeals) if currentMeals else "No meals collected yet."
    airesponse = BotResponse.confirm_response(conversation=conversations, query=user_query, collected_meals=avail_meals).content
    res = json.loads(airesponse)
    response = res["res"]
    if "meal" in res and res["meal"]:
        History.appendMealSlot(user_id, res["meal"])
    if res.get("flag", False):
        History.setChatState(user_id, "done")

    History.setHistory(userId=user_id, section="meal_chats", newConversation={
        "user": user_query,
        "assistant": response
    })

    return Response(content=response, media_type="text/plain", status_code=200)

# <--------- API --------->
@app.post("/chat")
def chat_handler(request: dict = Body(...)):
    user_id = request.get("id", "123456789")
    user_query = request.get("query")
    # user_calories = request.get("calories", 1600)
    # user_condition = request.get("conditions", ["Diabetes", "Acidity"])

    current_state = History.getChatState(user_id)
    chat_state = current_state.decode("utf-8") if isinstance(current_state, bytes) else current_state
    avail_conversations = []
    chats = History.getHistory(userId=user_id, section="meal_chats")
    if chats:
        for conv in chats.values():
            conversation = json.loads(conv)
            avail_conversations += [
                HumanMessage(content=conversation["user"]),
                AIMessage(content=conversation["assistant"])
            ]

    conversations = avail_conversations[-10:]

    match chat_state:
        case "collect":
            return collect_meals(user_id, user_query, conversations)
        case "confirm":
            return confirm_meals(user_id, user_query, conversations)
        case "done":
            return Response(content="Your meal plan has already been confirmed. Thank you!", media_type="text/plain", status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)