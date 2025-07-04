from langchain_core.messages import HumanMessage, AIMessage
from services.history import History
import json

def getLastChats(user_id: str, section: str = "chats") -> list:
    # Get the available Chats to check if we should generate summary or not
    avail_chats = History.getHistory(userId=user_id, section=section)
    if not avail_chats:
        return []

    conversations = []
    for conv in avail_chats.values():
        msg = json.loads(conv)
        conversations += [
            HumanMessage(content=msg["user"]),
            AIMessage(content=msg["assistant"])
        ]
    return conversations
