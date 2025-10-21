import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

# Import your modules
from models import ChatRequest
from chat_engine import get_response
from doc_engine import query_documents, initialize_index
from crisis import contains_crisis_keywords, get_safety_message
from logger import log_chat

# Load environment variables
load_dotenv()

# Lifespan context manager to initialize on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the document index
    print("🚀 Initializing document index...")
    success = initialize_index()
    if success:
        print("✓ Document index ready")
    else:
        print("⚠️ Warning: Document index initialization failed")
    yield
    # Shutdown: cleanup if needed
    print("👋 Shutting down...")

# Initialize FastAPI with lifespan
app = FastAPI(
    title="CHHARO Mental Health Chatbot API",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="chatbot-ui"), name="static")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "CHHARO API is running"}

# Home endpoint
@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("chatbot-ui/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h2>CHHARO API is running ✅</h2><p>Use POST /chat to interact</p>"
# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        user_query = request.query.strip()

        # Check for empty query
        if not user_query:
            return {"response": "Please type something to start the conversation.", "crisis": False}

        # Check crisis keywords FIRST
        if contains_crisis_keywords(user_query):
            response_text = get_safety_message()
            is_crisis = True
            log_chat(session_id, user_query, response_text, is_crisis)
            return {"response": response_text, "crisis": is_crisis}

        # Get document-based info (silently, for context only)
        doc_response = query_documents(user_query)

        # Get AI response with hidden document context
        # Only pass doc context to LLM, don't show it to user
        if doc_response and len(doc_response.strip()) > 10:
            context_query = f"User question: {user_query}\n\nBackground info (use this to inform your response, but keep your answer SHORT): {doc_response}"
        else:
            context_query = user_query
            
        llm_response = get_response(session_id, context_query)

        # Return ONLY the LLM response (no document text shown)
        response_text = llm_response
        is_crisis = False

        # Log the chat
        log_chat(session_id, user_query, response_text, is_crisis)

        return {"response": response_text, "crisis": is_crisis}
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {
            "response": "I'm having trouble processing your request. Please try again.",
            "crisis": False
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

