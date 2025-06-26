from langchain_core.messages import HumanMessage
from prompts import Prompt
import os

# LLM setup
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_tokens=None, api_key=os.getenv("GOOGLE_API_KEY"))

# from langchain_groq import ChatGroq
# llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0, max_tokens=None, api_key=os.getenv("GROQ_API_KEY"))
# llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0, max_tokens=None, api_key=os.getenv("GROQ_API_KEY"))

class BotResponse:
    @staticmethod
    def meal_response(conversation: list, query: str, collected_meals: str):
        prompt = Prompt.getMealPrompt(collected_meals)
        try:
            conversation.append(HumanMessage(content=prompt))
            conversation.append(HumanMessage(content=query))
            return llm.invoke(conversation)
        except Exception as e:
            return {"res": "Invalid response from model."+e}

    @staticmethod
    def confirm_response(conversation: list, query: str, collected_meals: str):
        prompt = Prompt.getConfirmPrompt(plan=collected_meals)
        try:
            conversation.append(HumanMessage(content=prompt))
            conversation.append(HumanMessage(content=query))
            return llm.invoke(conversation)
        except Exception as e:
            return {"res": "Invalid response from model." + e}