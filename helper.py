class Helper:
    # <------------------------- Textualize User Data ------------------------->
    # def textualize(data: dict):
    #     if isinstance(data, dict):
    #         data = UserBody(**data)  # Convert dict to UserBody

    #     template = f"""User Name: {data.name}
    #         Age: {data.age}
    #         State he belongs from: {', '.join(data.community)}
    #         Food Type Preference: {', '.join(data.foodType)}
    #         Disease / Conditions he suffers from: {', '.join(data.conditions)}
    #         Allergetic to: {', '.join(data.allergies) if data.allergies else "No Allergies"}
    #         """

    #     if data.goal is not None and isinstance(data.goal, dict):
    #         goals = UserGoals(**data.goal)
    #         template += f"""
    #         Calories Goal: {goals.calories}
    #         Carbs Goal: {goals.carbs}
    #         Fat Goal: {goals.fat}
    #         Protein Goal: {goals.protein}
    #         """
        
    #     return template

    def textualizeMeals(meals: dict) -> str:
        meal_str = []
        for slot, items in meals.items():
            slot_name = slot.replace("_", " ")
            if items:
                meal_str.append(f"{slot_name.capitalize()}: {' + '.join(items)}")
            else:
                meal_str.append(f"{slot_name.capitalize()}: No items.")
        
        return "\n".join(meal_str) if meal_str else "No meals collected yet."