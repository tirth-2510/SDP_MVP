from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from services.intent import getIntent
from services.history import History
from core.diet_guidance.advice import food_advice
from core.diet_guidance.generate import generate_plan
from core.diet_guidance.analyze import recall_analysis
from core.diet_guidance.improve import diet_improve
from core.sugar_support.sugar_control import sugar_support
from core.lifestyle.lifestyle_tip import lifestyle
from core.food_review.food_review import food
from core.medic.medication import medicine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello from Smart Diet Planner!"}

@app.post("/chat")
async def chat(request:dict = Body(...)):
    option = request.get("slot", "diet")
    user_data = request.get("data", {})
    query = request.get("query", "No query found")

    match option:
        case "diet":
            # Check current conversation Intent
            intent = History.getIntent(user_data["id"])

            # If intent doesnt exist, get it and set it in redis
            if intent is None:
                intent_res = getIntent(userId=user_data["id"],query=query)
                intent = intent_res.get("intent")
                if intent == "unknown":
                    return JSONResponse(content = {"response":"I'm sorry, I don't understand. Your request seems unrelated to my capabilities, Please ask a *Diet Guidance* related question.", "showSubOptions": True, "showOptions": False}, status_code=200)
                elif intent == "exit":
                    return JSONResponse(content = {"response":"Goodbye!", "showSubOptions": False, "showOptions": True}, status_code=200)
                History.setIntent(userId=user_data["id"], intent=intent)

            match intent:
                case "meal_advice":
                    return food_advice(query=query, data=user_data)
                case "diet_plan_today":
                    current_state = History.getChatState(user_data["id"])
                    if current_state is None:
                        History.setChatState(user_data["id"], "generate")
                    return generate_plan(query=query,data=user_data)
                case "diet_plan_week":
                    current_state = History.getChatState(user_data["id"])
                    if current_state is None:
                        History.setChatState(user_data["id"], "generate")
                    return generate_plan(query=query, data=user_data)
                case "analyze_diet_today":
                    current_state = History.getChatState(user_data["id"])
                    if current_state is None:
                        History.setChatState(user_data["id"], "analyze")
                    return recall_analysis(data=user_data, query=query)
                case "improve_current_diet":
                    current_state = History.getChatState(user_data["id"])
                    if current_state is None:
                        History.setChatState(user_data["id"], "improve")
                    return diet_improve(query=query,data=user_data)
            
        case "sugar_level":
            return sugar_support(data=user_data, query=query)
            
        case "lifestyle": 
            return lifestyle(data=user_data, query=query)
        
        case "food":
            return food(data=user_data, query=query)
        
        case "medicines":
            return medicine(data=user_data, query=query)
        
        case "log_parameters":
            return JSONResponse(content = {
                "response":"Will be available soon",
                "showSubOptions": False, 
                "showOptions": True}, 
                status_code=200)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)