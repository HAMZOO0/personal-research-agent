from mem0 import Memory
import traceback
import os
import atexit
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from mem0 import Memory

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
MEM0_CONFIG = {
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0_research_assistant",
            "embedding_model_dims": 384,
            "path": ":memory:",
        },
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dims": 384,
        },
    },
}

try:
    memory = Memory.from_config(MEM0_CONFIG)
    print("SUCCESS: Memory initialized")
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()