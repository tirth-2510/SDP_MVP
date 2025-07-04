from pydantic import BaseModel
from typing import Optional

class UserGoals(BaseModel):
    calories: float
    carbs: float
    fat: float
    protein: float
    
class UserBody(BaseModel):
    name: str
    age: int
    community: list
    goal: Optional[UserGoals] = None
    foodType: list
    conditions: list
    allergies: list

class ChatRequest(BaseModel):
    id: str
    knowledge_base: str
    section: str
    chunk_category: str
    query: str
    user_data: Optional[UserBody] = None