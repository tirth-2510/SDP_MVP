from fastapi.responses import JSONResponse
from services.history import History
from services.botresponse import BotResponse
from core.diet_guidance.collect import collect_plan
from core.diet_guidance.recall import recall_diet
from utils.text_formatter import Formatter
import json

def recall_analysis(data, query):
    # Get current Diet Plan
    current_diet_plan = History.getDietPlan(data["id"])

    # Get state as well
    chat_state = History.getChatState(data["id"])

    # If no user diet plan exists, first show the static message.
    if current_diet_plan is None:
        History.setChatState(data["id"], "collect")
        return JSONResponse(content={
            "response": f"Hello {data["name"]}, I'd like to understand your current food habits. That way, I can guide you better on the right changes to manage your diabetes.\nLet's begin with how you start your day — like a glass of water, tea/coffee, or anything else?\n",
            "showSubOptions": False,
            "showOptions": False}
        , status_code=200)
    
    # Something exists in current diet plan
    else:
        # Diet Plan is not complete yet,check if we are still collecting the plan
        if chat_state == "collect":
            return collect_plan(data, query)

        elif chat_state == "recall_diet_plan":
        
            if query.strip().lower() not in ["yes", "no"]:
                return JSONResponse(content={
                "response": f"Please reply with Yes or No only.",
                "showSubOptions": False,
                "showOptions": False}
                , status_code=200)
            
            else:
                
                # User said No. there are no changes
                if query.strip().lower() == "no":
                    # Get analysis
                    past_analysis = History.getDietRecallAnalysis(data["id"])

                    # If past analysis exist than show it
                    if past_analysis is not None:
                        History.setHistory(
                            userId=data["id"],
                            newConversation={
                                "user": query,
                                "assistant": past_analysis
                            }
                        )
                        History.deleteIntent(data["id"])
                        return JSONResponse(content={
                            "response": past_analysis,
                            "showSubOptions": True,
                            "showOptions": False
                        })

                    # Generate analysis
                    analysis_res = BotResponse.recall_analysis_response(
                        conditions=data["conditions"],
                        calories=data["calorie_goal"],
                        collected_meals=current_diet_plan
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

                    History.deleteChatState(data["id"])
                    History.deleteIntent(data["id"])
                    History.setPreferences(data["id"], preferences)
                    History.setDietRecallAnalysis(data["id"], res["res"])
                    return JSONResponse(content={
                        "response": res["res"],
                        "showSubOptions": True,
                        "showOptions": False
                    })
                
                # User said Yes, There are changes (Set State to recall and past state to analyze)
                else:
                    History.setChatState(data["id"], "recall")
                    History.setPastChatState(data["id"], "analyze")
                    return JSONResponse(content={
                        "response": "Great, please tell me what has changed so I can update the analysis.",
                        "showSubOptions": False,
                        "showOptions": False
                    })
                
        elif chat_state == "recall":
            return recall_diet(data, query)
            
        elif chat_state == "confirm_improvement":
            if query.strip().lower() not in ["yes", "no"]:
                return JSONResponse(content={
                "response": f"Please reply with Yes or No only.",
                "showSubOptions": False,
                "showOptions": False}
                , status_code=200)
            
            else:
                if query.strip().lower() == "no":
                    History.deleteChatState(data["id"])
                    History.deleteIntent(data["id"])
                    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": "Thank you. Have a nice day."})
                    return JSONResponse(content={
                        "response": "Thank you. Have a nice day.",
                        "showSubOptions": True,
                        "showOptions": False
                    })
                
                else:
                    past_improvements = History.getDietImprovement(data["id"])

                    # If past improvements exist than show it
                    if past_improvements is not None:
                        return JSONResponse(content={
                            "response": past_improvements,
                            "showSubOptions": True,
                            "showOptions": False
                        },
                        status_code=200)

                    # Else generate new improvements
                    improvement_res = BotResponse.improve_plan_response(
                        data=data,
                        collected_meals=current_diet_plan,
                        preferences=History.getPreferences(data["id"])
                    ).content

                    History.deleteChatState(data["id"])
                    History.deleteIntent(data["id"])
                    # save improvements.
                    History.setDietImprovement(data["id"], improvement_res)
                    History.setHistory(userId=data["id"], newConversation={"user": query, "assistant": improvement_res})
                    return JSONResponse(content={
                        "response": improvement_res,
                        "showSubOptions": True,
                        "showOptions": False
                    })
        
        elif chat_state == "analyze":
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