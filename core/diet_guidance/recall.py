from fastapi.responses import JSONResponse
from services.history import History
from services.botresponse import BotResponse
from services.conversations import getLastChats
from utils.text_formatter import Formatter
import json

def recall_diet(data: dict, query: str):
    state = History.getChatState(data["id"])
    
    # Recall Meal collection
    if state == "recall":
        conversations = getLastChats(data["id"])
        
        # Get the meal slots covered
        currentMeals = History.getDietPlan(data["id"])
        avail_meals = Formatter.meal_data(currentMeals) if currentMeals else "No meals collected yet."

        # Bot Response
        response = BotResponse.recall_response(
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

        # Everything Updated.
        if res.get("flag", False):
            current_diet_plan = History.getDietPlan(data["id"])
            diet_plan = Formatter.meal_data(current_diet_plan)
            past_state = History.getPastChatState(data["id"])

            # State wise Response generation
            if past_state == "analyze":
                analysis_res = BotResponse.recall_analysis_response(
                    conditions=data["conditions"],
                    calories=data["calorie_goal"],
                    collected_meals=diet_plan
                ).content

                try:
                    res = json.loads(analysis_res)
                except json.JSONDecodeError:
                    History.deleteIntent(data["id"])
                    return JSONResponse(content={
                        "response": "Sorry, there was an error analyzing your diet. Please try again later.",
                        "showSubOptions": True,
                        "showOptions": False},
                        status_code=200)
                
                # Save Preferences
                preferences = {"likes": res.get("likes", []), "dislikes": []}
                response_to_show = f"{res["res"]} \n Would you like to see Improvement in you diet?"

                History.setChatState(data["id"], "confirm_improvement")
                History.deletePastChatState(data["id"])
                History.setDietRecallAnalysis(data["id"], res["res"])
                History.setPreferences(data["id"], preferences)
                History.setHistory(
                    userId=data["id"],
                    newConversation={
                        "user": query,
                        "assistant": response_to_show
                    })

                return JSONResponse(content={
                    "response": response_to_show,
                    "showSubOptions": False,
                    "showOptions": False
                })
            
            elif past_state == "improve":
                preferences = History.getPreferences(data["id"])
                improve_res = BotResponse.improve_plan_response(
                    data=data,
                    collected_meals=diet_plan,
                    preferences=preferences
                ).content

                History.deleteChatState(data["id"])
                History.deletePastChatState(data["id"])
                History.deleteIntent(data["id"])
                History.setDietImprovement(data["id"], improve_res)
                History.setHistory(
                    userId=data["id"],
                    newConversation={
                        "user": query,
                        "assistant": improve_res
                    }
                )
                return JSONResponse(content={
                    "response": improve_res,
                    "showSubOptions": True,
                    "showOptions": False
                },
                status_code=200)
            
            elif past_state == "generate":
                preferences = History.getPreferences(data["id"])
                generate_res = BotResponse.generate_plan_response(
                    data=data,
                    current_meals=diet_plan,
                    preferences=preferences,
                    query=query
                ).content

                History.deleteChatState(data["id"])
                History.deletePastChatState(data["id"])
                History.setDietGeneration(data["id"], generate_res)
                History.setHistory(
                    userId=data["id"],
                    newConversation={
                        "user": query,
                        "assistant": generate_res
                    }
                )
                return JSONResponse(content={
                    "response": generate_res,
                    "showSubOptions": True,
                    "showOptions": False
                },
                status_code=200)

        # Save it in History.
        History.setHistory(
            userId=data["id"],
            newConversation={
                "user": query,
                "assistant": res.get("res", "")
            }
        )
        
        # Show Response and add it in History
        return JSONResponse(content = {
            "response":res.get("res", ""),
            "showSubOptions": res.get("showSubOptions", False),
            "showOptions": res.get("showOptions", False)},
            status_code=200)