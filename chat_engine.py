import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load .env
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.6,
    max_tokens=150
)

# Store session chat histories
session_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    # Get or create chat history for a session.
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# Create prompt template for mental health support
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a compassionate mental health support chatbot for Bhutan. 

IMPORTANT RULES:
- Keep responses SHORT (2-3 sentences maximum)
- Be warm and empathetic but CONCISE
- Don't repeat greetings like "Kuzu zangpo" in every message
- Only use "Kuzu zangpo" for the FIRST message to a new user
- NO numbered lists or bullet points
- Focus on listening and asking ONE follow-up question
- Encourage professional help when appropriate
- Use natural, conversational language

Example good responses:
"I hear you. It's completely normal to feel this way sometimes. What's been on your mind lately?"
"That sounds really difficult. Would you like to talk more about what's making you feel this way?"
"I'm here to listen. Sometimes just talking about it can help."

DO NOT give long advice lists or step-by-step instructions unless specifically asked."""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Create the conversational chain
chain = prompt | llm

# Wrap with message history
conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)
def get_response(session_id: str, user_query: str) -> str:
    """
    Get a response from the chatbot with conversation history.
    
    Args:
        session_id: Unique identifier for the conversation session
        user_query: The user's input query (may include document context)
        
    Returns:
        The chatbot's response as a string
    """
    try:
        response = conversational_chain.invoke(
            {"input": user_query},
            config={"configurable": {"session_id": session_id}}
        )
        return response.content
    except Exception as e:
        print(f"Error in get_response: {e}")
        return "I'm having trouble right now. Could you try saying that again?"

def clear_session(session_id: str) -> bool:
    """Clear chat history for a specific session."""
    if session_id in session_store:
        del session_store[session_id]
        return True
    return False
