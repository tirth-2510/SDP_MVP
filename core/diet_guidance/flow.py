from services.intent import getIntent
from core.diet_guidance.advice import food_advice
from core.diet_guidance.generate import generate_plan
from core.diet_guidance.analyze import recall_analysis
from core.diet_guidance.improve import diet_improve

# Official First Flow
def DietGuidanceFlow(data):
    while True:
        print("""Bot: Do you need advice for Breakfast, Lunch, Dinner, or a Snack?\nOr do you want a Diet Plan for Today or the Week?\nOr do you want me to analyze your diet for Today?\nOr would you like to view suggestions to improve your current diet?\n""")
        user_input = input("User: ").strip().lower()
        if user_input in ["exit", "quit", "e", "q"]:
            print("Bot: Good Bye")
            return
        intent_res = getIntent(user_input)
        intent = intent_res.get("intent")
        match intent:
            case "meal_advice":
                food_advice(user_input, data=data)
            
            case "diet_plan_today":
                generate_plan(query=user_input)
            
            case "diet_plan_week":
                generate_plan(query=user_input)
            
            case "analyze_diet_today":
                recall_analysis(data=data, query=query)
            
            case "improve_current_diet":
                diet_improve(data=data,query=user_input)


