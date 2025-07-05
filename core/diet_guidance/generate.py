from fastapi.responses import JSONResponse
from core.diet_guidance.collect import collect_plan
from core.diet_guidance.recall import recall_diet
from services.botresponse import BotResponse
from services.history import History
from utils.text_formatter import Formatter

def generate_plan(data, query):
    # Get current Diet Plan
    current_diet_plan = History.getDietPlan(data["id"])

    # Get state as well
    chat_state = History.getChatState(data["id"])

    # If no user diet plan exists, trigger collection flow
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
                    # Get Plan Generation
                    past_generation = History.getDietGeneration(data["id"])

                    # If past improvement exist than show it
                    if past_generation is not None:
                        History.setHistory(
                            userId=data["id"],
                            newConversation={
                                "user": query,
                                "assistant": past_generation
                            }
                        )
                        History.deleteIntent(data["id"])
                        return JSONResponse(content={
                            "response": past_generation,
                            "showSubOptions": True,
                            "showOptions": False
                        })
                    
                    preferences = History.getPreferences(data["id"])
                    
                    # Generate Diet Plan
                    generation_res = BotResponse.generate_plan_response(
                        data=data,
                        current_meals=current_diet_plan,
                        preferences=preferences,
                        query=query
                    ).content

                    History.deleteChatState(data["id"])
                    History.deleteIntent(data["id"])
                    History.setDietGeneration(data["id"], generation_res)
                    History.setHistory(
                        userId=data["id"], 
                        newConversation={"user": query, "assistant": generation_res}
                    )
                    return JSONResponse(content={
                        "response": generation_res,
                        "showSubOptions": True,
                        "showOptions": False
                    })
                
                # User said Yes, There are changes (Set State to recall and past state to analyze)
                else:
                    History.setChatState(data["id"], "recall")
                    History.setPastChatState(data["id"], "generate")
                    return JSONResponse(content={
                        "response": "Great, please tell me what has changed so I can update the Generation.",
                        "showSubOptions": False,
                        "showOptions": False
                    })
                
        elif chat_state == "recall":
            return recall_diet(data, query)

        elif chat_state == "generate":
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
