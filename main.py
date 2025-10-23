import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from models import ChatRequest
from chat_engine import get_response
from crisis import contains_crisis_keywords, get_safety_message
from logger import log_chat

# Load environment variables
load_dotenv()

PORT = os.getenv("PORT", "10000")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY not found!")
    print("Please set it in Render Environment Variables")
    sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌟 Backend API started successfully")
    yield
    print("👋 Backend API shutting down")

app = FastAPI(
    title="CHHARO Mental Health Chatbot API",
    description="Backend API for CHHARO mental health support chatbot",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chharo-mentalhealthchatbot.onrender.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return JSONResponse({
        "status": "online",
        "service": "CHHARO Mental Health Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "docs": "/docs"
        }
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "CHHARO Backend API",
        "groq_configured": bool(GROQ_API_KEY)
    })

@app.post("/chat")
async def chat(request: ChatRequest):
    
    try:
        session_id = request.session_id
        user_query = request.query.strip()
        
        if not user_query:
            return JSONResponse({
                "response": "Please type something.",
                "crisis": False
            })
        
        # Check for crisis keywords
        if contains_crisis_keywords(user_query):
            print("⚠️ CRISIS keywords detected")
            response_text = get_safety_message()
            log_chat(session_id, user_query, response_text, True)
            return JSONResponse({
                "response": response_text,
                "crisis": True
            })
        doc_response = "" 
        try: 
            from doc_engine import query_documents 
            doc_response = query_documents(user_query) 
            if doc_response: print(f"📚 Document context: {len(doc_response)} chars") except Exception as e: print(f"ℹ️ No document search: {e}") 
            # Build query with context if available 
            context_query = ( 
                f"User question: {user_query}\n\nBackground info: {doc_response}" 
                if doc_response and len(doc_response.strip()) > 10 
                else user_query 
            )
        # Get LLM response
        print("🤖 Calling Groq LLM...")
        llm_response = get_response(session_id, context_query)
        print(f"✅ Response generated: {len(llm_response)} chars")
        
        # Log the interaction
        log_chat(session_id, user_query, llm_response, False)
        
        return JSONResponse({
            "response": llm_response,
            "crisis": False
        })
        
    except Exception as e:
        print(f"❌ ERROR in /chat endpoint:")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "response": "I'm having trouble right now. Please try again in a moment.",
                "crisis": False,
                "error": str(e)
            }
        )

@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 50)
    print("🎉 BACKEND API IS READY!")
    print(f"📡 Listening on http://0.0.0.0:{PORT}")
    print("🔗 Frontend can now connect to this API")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    try:
        port = int(PORT)
        print(f"🌐 Starting server on port {port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
