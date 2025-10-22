import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Directories
DATA_DIR = "./data"
PERSIST_DIR = "./storage"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure LLM and Embeddings
Settings.llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY
)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Global query engine
query_engine = None

def initialize_index():
    """
    Load or create a vector store index from the data directory.
    """
    global query_engine

    try:
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            print("Loading existing index from storage...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            print("✓ Index loaded successfully")
        else:
            print("Creating new index from documents...")
            if not os.path.exists(DATA_DIR):
                raise FileNotFoundError(f"Data directory '{DATA_DIR}' not found")

            documents = SimpleDirectoryReader(DATA_DIR).load_data()

            if not documents:
                raise ValueError(f"No documents found in '{DATA_DIR}'")

            print(f"Found {len(documents)} document(s)")
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            print(f"✓ Index created and saved to '{PERSIST_DIR}'")

        # Create query engine with concise responses
        query_engine = index.as_query_engine(
            similarity_top_k=2,  # Reduced from 3
            response_mode="compact",
            text_qa_template=(
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Given the context, answer this briefly in 1-2 sentences: {query_str}\n"
            )
        )

        return True

    except Exception as e:
        print(f"✗ Error initializing index: {e}")
        return False


def query_documents(user_query: str) -> str:
    """
    global query_engine

    # Initialize index if not already
    if query_engine is None:
        success = initialize_index()
        if not success:
            return ""  # Return empty string on error, don't expose error to user

    try:
        if not user_query.strip():
            return ""

        response = query_engine.query(user_query)
        result = str(response).strip()
        
        # Return only if response is meaningful and not too long
        if len(result) > 20 and len(result) < 500:
            return result
        return ""

    except Exception as e:
        print(f"Error querying documents: {e}") """
        return ""  # Silent failure, just return empty


def reset_index():
    """
    Clear the cached index for regeneration.
    """
    global query_engine

    try:
        if os.path.exists(PERSIST_DIR):
            import shutil
            shutil.rmtree(PERSIST_DIR)
            print(f"✓ Deleted cached index at '{PERSIST_DIR}'")

        query_engine = None
        print("✓ Index reset complete")
        return True
    except Exception as e:
        print(f"✗ Error resetting index: {e}")
        return False
