import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "./data"
PERSIST_DIR = "./storage"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

query_engine = None
_settings_initialized = False

def _initialize_settings():
    """Initialize LLM settings only when needed"""
    global _settings_initialized
    if not _settings_initialized:
        print("🔧 Initializing LLM settings...")
        Settings.llm = Groq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder="./model_cache"
        )
        _settings_initialized = True

def initialize_index():
    global query_engine
    try:
        _initialize_settings()
        
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            print("📂 Loading existing index...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
        else:
            print("📚 Creating new index from documents...")
            documents = SimpleDirectoryReader(DATA_DIR).load_data()
            index = VectorStoreIndex.from_documents(documents)
            os.makedirs(PERSIST_DIR, exist_ok=True)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            print("✅ Index created and persisted")
        
        query_engine = index.as_query_engine(similarity_top_k=2, response_mode="compact")
        return True
    except Exception as e:
        print(f"❌ Error initializing index: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Return result if it's meaningful
        return result if 20 < len(result) < 500 else ""
    except Exception as e:
        print(f"❌ Error querying documents: {e}")
        return ""
