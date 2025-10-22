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
    print("🚀 Initializing document index...")
    success = initialize_index()
    if success:
        print("✓ Document index ready")
    else:
        print("⚠️ Warning: Document index initialization failed")
    yield
    print("👋 Shutting down...")

# App instance
app = FastAPI(title="CHHARO Mental Health Chatbot API", lifespan=lifespan)

# CORS middleware
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

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        user_query = request.query.strip()

        if not user_query:
            return {"response": "Please type something to start the conversation.", "crisis": False}

        if contains_crisis_keywords(user_query):
            response_text = get_safety_message()
            is_crisis = True
            log_chat(session_id, user_query, response_text, is_crisis)
            return {"response": response_text, "crisis": is_crisis}

        doc_response = query_documents(user_query)

        if doc_response and len(doc_response.strip()) > 10:
            context_query = f"User question: {user_query}\n\nBackground info (use this to inform your response, but keep your answer SHORT): {doc_response}"
        else:
            context_query = user_query

        llm_response = get_response(session_id, context_query)
        response_text = llm_response
        is_crisis = False
        log_chat(session_id, user_query, response_text, is_crisis)

        return {"response": response_text, "crisis": is_crisis}

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {"response": "I'm having trouble processing your request. Please try again.", "crisis": False}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
