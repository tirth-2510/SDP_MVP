from fastapi.responses import JSONResponse
from services.history import History
from services.botresponse import BotResponse
from services.conversations import getLastChats
from utils.text_formatter import Formatter
import json

def collect_plan(data, query):
    state = History.getChatState(data["id"])

    # Meal collection loop
    if state == "collect":
        conversations = getLastChats(data["id"])

        # Get the meal slots covered
        collected_meals = History.getDietPlan(data["id"])
        avail_meals = Formatter.meal_data(collected_meals) if collected_meals else "No meals collected yet."

        # Bot Response
        response = BotResponse.collection_response(
            conversation=conversations,
            query=query,
            collected_meals=avail_meals
        ).content

        # Parse JSON response
        try:
            res = json.loads(response)
        except json.JSONDecodeError:
            return JSONResponse(content={"response": "Sorry there was an error processing your input. Can you enter it again.\n",
            "showSubOptions": False,
            "showOptions": False}, 
            status_code=200)

        # Append meal slot if meal
        if "meal" in res and res["meal"]:
            History.appendMealSlot(data["id"], res["meal"])
        
        # All meals Collected?
        if res.get("flag", False):
            History.deleteChatState(data["id"])
            current_diet_plan = History.getDietPlan(data["id"])
            diet_plan = Formatter.meal_data(current_diet_plan)
            response_to_show = f"{data["name"]}, Here is the summary of your current diet plan.\n\n{diet_plan}\n\nHave you made any changes to your diet since then? Please reply with yes or no.\n"
            History.setHistory(
                userId=data["id"],
                newConversation={
                    "user": query,
                    "assistant": response_to_show
                }
            )
            History.setChatState(data["id"], "recall_diet_plan")
            return JSONResponse(content={
                "response":response_to_show,
                "showSubOptions": False,
                "showOptions": False}, 
                status_code=200)
        
        History.setHistory(
            userId=data["id"],
            newConversation={
                "user": query,
                "assistant": res.get("res", "")
            }
        )
        # Show Response and add it in History
        return JSONResponse(content = {"response":res.get("res", ""),
                                       "showSubOptions": res.get("showSubOptions", False),
                                       "showOptions": res.get("showOptions", False)},
                                        status_code=200)
        