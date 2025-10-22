import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "./data"
PERSIST_DIR = "./storage"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

Settings.llm = Groq(model="llama-3-1b-instant", api_key=GROQ_API_KEY)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

query_engine = None

def initialize_index():
    global query_engine
    try:
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
        else:
            documents = SimpleDirectoryReader(DATA_DIR).load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
        query_engine = index.as_query_engine(similarity_top_k=2, response_mode="compact")
        return True
    except Exception as e:
        print(f"Error initializing index: {e}")
        return False

def query_documents(user_query: str) -> str:
    global query_engine
    if query_engine is None:
        if not initialize_index():
            return ""
    try:
        if not user_query.strip():
            return ""
        response = query_engine.query(user_query)
        result = str(response).strip()
        return result if 20 < len(result) < 500 else ""
    except Exception as e:
        print(f"Error querying documents: {e}")
        return ""
