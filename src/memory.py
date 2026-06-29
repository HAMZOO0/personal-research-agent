import os
import atexit
os.environ["ANONYMIZED_TELEMETRY"] = "False"   # stops mem0 spawning a second Qdrant client

from mem0 import Memory
from src.config import MEM0_CONFIG

MEMORY_INIT_ERROR = None
try:
    MEMORY = Memory.from_config(MEM0_CONFIG)
    print("SUCCESS: Memory initialized")
except Exception as e:
    import traceback
    MEMORY = None
    MEMORY_INIT_ERROR = traceback.format_exc()
    print(f"Memory init error: {e}")


def get_memories(query: str, user_id: str, limit: int = 5) -> str:
    """Retrieve and format memories for a specific user and query."""
    if MEMORY is None:
        return "(memory system unavailable)"
    
    try:
        try:
            search_results = MEMORY.search(
                query=query,
                filters={"user_id": user_id},
                limit=limit,
            )
        except TypeError:
            search_results = MEMORY.search(
                query=query,
                user_id=user_id,
                limit=limit,
            )

        items = search_results.get("results", []) if isinstance(search_results, dict) else search_results
        memories = [
            f"- {item['memory']}"
            for item in items
            if isinstance(item, dict) and item.get("memory")
        ]
        return "\n".join(memories) if memories else "(no prior memories yet)"
    except Exception as e:
        print(f"Error searching memory: {e}")
        return "(error retrieving memories)"


def add_memory(user_id: str, user_message: str, assistant_reply: str) -> None:
    """Store the conversation turn into long-term memory."""
    if MEMORY is None:
        return
    try:
        result = MEMORY.add(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_reply},
            ],
            user_id=user_id,
        )
        print(f"Memory saved: {result}")
    except Exception as e:
        import traceback
        print(f"Error adding to memory: {e}")
        traceback.print_exc()


def getAllMemory(user_id: str) -> list:
    """Fetch all memories stored for a user ID."""
    if MEMORY is None:
        return []
    # Try newer API (filters dict) first, fall back to legacy (user_id kwarg)
    try:
        result = MEMORY.get_all(filters={"user_id": user_id})
        # If result looks empty, retry with legacy API
        items = result.get("results", result) if isinstance(result, dict) else result
        if not items:
            raise ValueError("empty — trying legacy API")
        return result
    except Exception:
        pass
    try:
        return MEMORY.get_all(user_id=user_id)
    except Exception as exc:
        print(f"Error getting all memories: {exc}")
        return []


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
