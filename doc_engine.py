import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
IS_RENDER = os.getenv("RENDER")  # Render sets this automatically

Settings.llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY
)

# Only load embeddings if NOT on Render
if not IS_RENDER:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def query_documents(user_query: str) -> str:
    if IS_RENDER:
        return ""  # Disabled on Render
    
    # Your existing code here...
    # (keep your current implementation for local use)
