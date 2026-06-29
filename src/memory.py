import sqlite3
import json
import atexit
from pathlib import Path
from datetime import datetime

DB_PATH = Path("./memory.db")
MEMORY_INIT_ERROR = None

_EXTRACT_SYSTEM = (
    "Extract 0-3 personal facts about the user from the message. "
    "Only extract clear facts: name, location, profession, interests, goals. "
    "Return a JSON array of strings only. If nothing factual, return [].\n"
    'Example: ["Name is Hamza", "From Pakistan", "Software engineer"]'
)

# Models for fact extraction — separate buckets from chat cascade
_EXTRACT_MODELS = [
    "groq:llama-3.3-70b-versatile",
    "groq:qwen/qwen3-32b",
    "groq:qwen/qwen3.6-27b",
]


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   TEXT    NOT NULL,
            memory    TEXT    NOT NULL,
            created_at TEXT   DEFAULT (datetime('now'))
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_uid ON memories(user_id)")
    c.commit()
    return c


try:
    _conn().close()
    MEMORY = True
    print("SUCCESS: Memory initialized (SQLite)")
except Exception as e:
    MEMORY = None
    MEMORY_INIT_ERROR = str(e)
    print(f"Memory init error: {e}")


def _extract_facts(user_message: str) -> list:
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage, SystemMessage

    for model_id in _EXTRACT_MODELS:
        try:
            resp = init_chat_model(model_id).invoke([
                SystemMessage(_EXTRACT_SYSTEM),
                HumanMessage(user_message[:400]),
            ])
            raw = resp.content.strip()
            start, end = raw.find("["), raw.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
            return []
        except Exception as e:
            print(f"Extraction failed ({model_id}): {e}")
    return []


def add_memory(user_id: str, user_message: str, assistant_reply: str) -> None:
    if not MEMORY:
        return
    try:
        facts = _extract_facts(user_message)
        if facts:
            with _conn() as c:
                c.executemany(
                    "INSERT INTO memories (user_id, memory) VALUES (?, ?)",
                    [(user_id, str(f)) for f in facts],
                )
            print(f"Memory saved: {facts}")
        else:
            print("Memory: no new facts")
    except Exception as e:
        print(f"Memory add failed: {e}")


def get_memories(query: str, user_id: str, limit: int = 5) -> str:
    if not MEMORY:
        return "(memory system unavailable)"
    try:
        with _conn() as c:
            rows = c.execute(
                "SELECT memory FROM memories WHERE user_id=? ORDER BY id DESC LIMIT 50",
                (user_id,),
            ).fetchall()
        if not rows:
            return "(no prior memories yet)"
        memories = [r[0] for r in rows]
        # Keyword relevance ranking
        query_words = set(query.lower().split())
        ranked = sorted(memories, key=lambda m: len(query_words & set(m.lower().split())), reverse=True)
        return "\n".join(f"- {m}" for m in ranked[:limit])
    except Exception as e:
        print(f"Memory search failed: {e}")
        return "(error retrieving memories)"


def getAllMemory(user_id: str) -> list:
    if not MEMORY:
        return []
    try:
        with _conn() as c:
            rows = c.execute(
                "SELECT memory, created_at FROM memories WHERE user_id=? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        return [{"memory": r[0], "created_at": r[1]} for r in rows]
    except Exception as e:
        print(f"getAllMemory failed: {e}")
        return []


atexit.register(lambda: None)
