import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from models import ChatRequest
from chat_engine import get_response
from doc_engine import query_documents, initialize_index
from crisis import contains_crisis_keywords, get_safety_message
from logger import log_chat

# Load environment variables
load_dotenv()

# Startup/shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # Lazy load index on first query to save memory

app = FastAPI(title="CHHARO Mental Health Chatbot API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "CHHARO API is running"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h2>CHHARO API is running ✅</h2><p>Use POST /chat to interact with the chatbot</p>"

index_initialized = False

@app.post("/chat")
async def chat(request: ChatRequest):
    global index_initialized
    try:
        session_id = request.session_id
        user_query = request.query.strip()
        if not user_query:
            return {"response": "Please type something.", "crisis": False}

        if contains_crisis_keywords(user_query):
            response_text = get_safety_message()
            log_chat(session_id, user_query, response_text, True)
            return {"response": response_text, "crisis": True}

        # Lazy load index
        if not index_initialized:
            print("🧠 Loading index...")
            initialize_index()
            index_initialized = True

        doc_response = query_documents(user_query)
        context_query = (
            f"User question: {user_query}\n\nBackground info: {doc_response}"
            if doc_response and len(doc_response.strip()) > 10
            else user_query
        )
        llm_response = get_response(session_id, context_query)
        log_chat(session_id, user_query, llm_response, False)
        return {"response": llm_response, "crisis": False}

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {"response": "I'm having trouble processing your request.", "crisis": False}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
