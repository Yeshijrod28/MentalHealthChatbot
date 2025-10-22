import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from models import ChatRequest
from chat_engine import get_response
from crisis import contains_crisis_keywords, get_safety_message
from logger import log_chat

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Server starting - lightweight mode (no document indexing)")
    yield
    print("👋 Server shutting down")

app = FastAPI(title="CHHARO Mental Health Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if os.path.exists("chatbot-ui"):
    app.mount("/static", StaticFiles(directory="chatbot-ui"), name="static")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "CHHARO API is running"}

@app.get("/")
async def home():
    if os.path.exists("chatbot-ui/index.html"):
        return FileResponse("chatbot-ui/index.html")
    return HTMLResponse("<h2>CHHARO API is running ✅</h2><p>Use POST /chat to interact</p>")

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        user_query = request.query.strip()
        
        if not user_query:
            return {"response": "Please type something.", "crisis": False}
        
        if contains_crisis_keywords(user_query):
            response_text = get_safety_message()
            log_chat(session_id, user_query, response_text, True)
            return {"response": response_text, "crisis": True}
        
        llm_response = get_response(session_id, user_query)
        log_chat(session_id, user_query, llm_response, False)
        
        return {"response": llm_response, "crisis": False}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"response": "I'm having trouble right now. Please try again.", "crisis": False}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
