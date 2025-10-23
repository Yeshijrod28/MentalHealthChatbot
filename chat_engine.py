import os
from dotenv import load_dotenv
""" 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
"""
from llama_index.llms.groq import Groq
# Load .env
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
)

# Store session chat histories
session_store = {}

system_prompt = (
    "You are a compassionate Bhutanese mental health support chatbot.\n\n"
    "RULES:\n"
    "- Keep responses SHORT (2-3 sentences maximum)\n"
    "- Be warm and empathetic but CONCISE\n"
    "- Only use 'Kuzu zangpo' once per new user\n"
    "- No bullet points or numbered lists\n"
    "- Ask one gentle follow-up question\n"
    "- Encourage professional help when appropriate\n"
)
def get_response(session_id: str, user_query: str) -> str:
    """Get a response from the chatbot with conversation history."""
    try:
        # Load chat history for context
        history = session_store.get(session_id, [])

        # Build the prompt including history
        full_prompt = SYSTEM_PROMPT + "\n"
        for msg in history[-5:]:
            full_prompt += f"User: {msg['user']}\nBot: {msg['bot']}\n"
        full_prompt += f"User: {user_query}\nBot:"

        # Query the LLM
        response = llm.complete(full_prompt)
        answer = response.text.strip()

        # Save conversation
        session_store.setdefault(session_id, []).append({
            "user": user_query,
            "bot": answer
        })

        return answer

    except Exception as e:
        print(f"Error in get_response: {e}")
        return "I'm sorry, something went wrong. Could you try again?"

def clear_session(session_id: str) -> bool:
    """Clear chat history for a session."""
    if session_id in session_store:
        del session_store[session_id]
        return True
    return False

"""
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
