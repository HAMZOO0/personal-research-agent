import warnings
warnings.filterwarnings("ignore")

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

SYSTEM_PROMPT_TEMPLATE = """You are an expert research assistant with access to real-time web search and memory of past research sessions.

Your job is to help users research any topic deeply and accurately.

MEMORY CONTEXT FROM PAST SESSIONS:
{memory}

BEHAVIOR:
- Always break complex questions into smaller sub-questions before answering
- Search for the most recent and relevant information
- Cross-reference multiple sources before giving a conclusion
- Use the memory context above to build on what the user has already researched
- Never ask the user to repeat context that already exists in memory
- If a topic was researched before, mention it and connect it to the new query
- If memory is empty, treat this as a fresh session

OUTPUT FORMAT:
- Give a clear structured answer with sections
- Always cite your sources with links
- End every response with 3 follow-up questions the user might want to explore
- If the research is complex, summarize key findings at the top

TONE:
- Be precise and factual, not conversational
- Avoid filler phrases
- Be concise but never skip important details

If you do not know something, say so clearly. Never hallucinate facts or sources."""

# --- Init model ---
try:
    model = init_chat_model("groq:qwen/qwen3-32b")
    print("SUCCESS: Model initialized")
except Exception as e:
    model = None
    print(f"Model init error: {e}")

# --- Init memory ---
try:
    MEMORY = Memory.from_config(MEM0_CONFIG)
    print("SUCCESS: Memory initialized")
except Exception as e:
    MEMORY = None
    print(f"Memory init error: {e}")


def _format_memories(search_results) -> str:
    items = search_results.get("results", []) if isinstance(search_results, dict) else search_results
    memories = [
        f"- {item['memory']}"
        for item in items
        if isinstance(item, dict) and item.get("memory")
    ]
    return "\n".join(memories) if memories else "(no prior memories yet)"


def _close_memory() -> None:
    if MEMORY is None:
        return
    try:
        MEMORY.vector_store.client.close()
    except Exception:
        pass
    try:
        MEMORY.close()
    except Exception:
        pass

atexit.register(_close_memory)


def chat(user_id: str, user_message: str) -> str:
    if MEMORY is None:
        return "Setup error: could not initialize Mem0."
    if model is None:
        return "Setup error: could not initialize model."

    try:
        search_results = MEMORY.search(
            query=user_message,
            filters={"user_id": user_id},
            limit=5
        )
        memory_context = _format_memories(search_results)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE.format(memory=memory_context)),
            HumanMessage(content=user_message),
        ]

        response = model.invoke(messages)
        reply = response.content

        MEMORY.add(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": reply},
            ],
               user_id=user_id,

        )

        return reply

    except Exception as exc:
        return f"Error: {exc}"


def getAllMemory(user_id: str):
    if MEMORY is None:
        return []
    try:
        return MEMORY.get_all(filters={"user_id": user_id})
    except Exception as exc:
        return []