import os
from dotenv import load_dotenv
from langchain_milvus import Zilliz
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pymongo import MongoClient
from utils.text_formatter import Formatter

# Load environment variables
load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GOOGLE_API_KEY"))

mongoClient = MongoClient(os.getenv("MONGODB_URI"))
db=mongoClient["sdp_chatbot"]
collection=db["foodItems"]

class milvusDB():
    @staticmethod
    def vectorstore(document_id: str):
        return Zilliz(
            collection_name=document_id,
            connection_args={"uri": os.getenv("ZILLIZ_URI_ENDPOINT"), "token": os.getenv("ZILLIZ_TOKEN")},
            index_params={"index_type": "IVF_PQ", "metric_type": "COSINE"},
            embedding_function=embeddings,
        )
            
    @staticmethod
    def setSummary(userId: str, summary: str):
        vs = milvusDB.vectorstore("UserSummaries")
        vs.add_texts(texts=[summary], metadatas=[{"chunk_category": userId}])
        
class mongoDB():
    def getLastConv(id: str, sec: str):
        return collection.find_one({"userId": id, "section": sec}, sort=[("timestamp", -1)])
    
    def setSumPref(userId: str, summary: str, preferences: str):
        collection.find_one_and_update(
            {"userId": userId},
            {"$set": {"summary": summary, "preferences": preferences}},
            upsert=True
        )
