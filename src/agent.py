import os
import re
import sys
import json
import asyncio
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

from src.config import SYSTEM_PROMPT_TEMPLATE, MODEL_CASCADE
from src.memory import get_memories, add_memory
from src.tools.search import web_search_tool
from src.tools.arxiv import arxiv_search_tool, fetch_arxiv_paper_tool
from src.tools.youtube import youtube_search_tool, youtube_transcript_tool
from src.tools.github import github_search_tool

# Build the model pool at startup — skip any that fail to initialize.
_model_pool: list = []
for _mid in MODEL_CASCADE:
    try:
        _model_pool.append(init_chat_model(_mid))
        print(f"SUCCESS: Initialized {_mid}")
    except Exception as _e:
        print(f"WARNING: Could not initialize {_mid}: {_e}")


# --- Direct LangChain tools (no subprocess, no MCP overhead) ---

@tool
def web_search(query: str) -> str:
    """Search the web for the latest information on a topic."""
    return web_search_tool(query)

@tool
def arxiv_search(query: str) -> str:
    """Search arXiv for research papers on a topic.
    Returns paper IDs, titles, authors, publication dates, abstracts, and URLs.
    Use this FIRST to discover relevant papers, then use fetch_arxiv_paper to read them fully.
    """
    return arxiv_search_tool(query)

@tool
def fetch_arxiv_paper(arxiv_id_or_url: str) -> str:
    """Download and extract the full text of a specific arXiv paper by its ID or URL.

    Use when you have an arXiv ID (e.g. '2310.01526') or an arXiv URL
    and want to read the paper's abstract, methods, or main findings in full.
    """
    return fetch_arxiv_paper_tool(arxiv_id_or_url)

@tool
def youtube_search(query: str) -> str:
    """Search YouTube for videos related to a topic.
    Returns a JSON string with video titles, URLs, and video IDs.
    """
    return youtube_search_tool(query)

@tool
def youtube_transcript(video_id: str) -> str:
    """Fetch the transcript of a YouTube video by its video ID or URL."""
    return youtube_transcript_tool(video_id)

@tool
def github_search(query: str) -> str:
    """Search GitHub for repositories matching a query.
    Returns a JSON string of repos with name, stars, URL, and description.
    """
    return github_search_tool(query)


ALL_TOOLS = [web_search, arxiv_search, fetch_arxiv_paper, youtube_search, youtube_transcript, github_search]
_ALL_TOOL_MAP = {t.name: t for t in ALL_TOOLS}


def _repair_json(s: str) -> str:
    """Add missing closing braces to truncated JSON strings."""
    s = s.strip()
    opens = s.count('{') - s.count('}')
    s += '}' * max(opens, 0)
    return s


def _parse_malformed_call(error_str: str):
    """
    Groq rejects tool calls when the model emits them as raw text instead of
    structured JSON. Several formats appear in practice:

        <function=youtube_search>{"query": "graph rag"</function>   ← truncated JSON
        <function=web_search={"query": "foo"}</function>
        <function=web_search {"query": "foo"}></function>
        tool call validation failed: attempted to call tool 'web_search {"query": "foo"}'

    Returns (tool_name, args_dict) or (None, {}) if no match.
    """
    # Pattern 1: <function=NAME>{possibly-truncated JSON}</function>
    m = re.search(r'<function=(\w+)>(\{[^<]*)</function>', error_str, re.DOTALL)
    if m:
        try:
            return m.group(1), json.loads(_repair_json(m.group(2)))
        except Exception:
            pass

    # Pattern 2: <function=NAME[= >{JSON}>  (with optional > before </function>)
    m = re.search(r'<function=(\w+)[\s=>]+(\{.+?\})>?<', error_str, re.DOTALL)
    if m:
        try:
            return m.group(1), json.loads(m.group(2))
        except Exception:
            pass

    # Pattern 3: tool call validation failed: attempted to call tool 'NAME {JSON}'
    m = re.search(r"attempted to call tool '(\w+)\s+(\{.+?\})'", error_str, re.DOTALL)
    if m:
        try:
            return m.group(1), json.loads(m.group(2))
        except Exception:
            pass

    # Pattern 4: any <function=NAME ...{"key":"val"}...  (complete JSON anywhere)
    m = re.search(r'<function=(\w+)[^{]*(\{[^{}]+\})', error_str)
    if m:
        try:
            return m.group(1), json.loads(m.group(2))
        except Exception:
            pass

    return None, {}


def _is_rate_limit(exc: Exception) -> bool:
    return "rate_limit_exceeded" in str(exc) or "429" in str(exc)


def chat(user_id: str, user_message: str, enabled_tools: list = None) -> dict:
    if not _model_pool:
        return {"reply": "Setup error: no models could be initialized.", "github_results": [], "youtube_results": []}

    _state = {"idx": 0}

    try:
        command_instruction = ""
        clean_message = user_message.strip()
        forced_tool = None

        if clean_message.startswith("/"):
            parts = clean_message.split(" ", 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            if cmd in ["/websearch", "/search"]:
                command_instruction = f"Search the web for: {args}. "
                clean_message = args
                forced_tool = "web_search"
            elif cmd in ["/github", "/git"]:
                command_instruction = f"Search GitHub for: {args}. "
                clean_message = args
                forced_tool = "github_search"
            elif cmd in ["/youtube", "/yt"]:
                command_instruction = f"Find YouTube videos about: {args}. "
                clean_message = args
                forced_tool = "youtube_search"
            elif cmd in ["/arxiv", "/paper"]:
                command_instruction = f"Fetch this arXiv paper: {args}. "
                clean_message = args
                forced_tool = "fetch_arxiv_paper"
            elif cmd in ["/asearch", "/papers"]:
                command_instruction = f"Search arXiv for research papers about: {args}. "
                clean_message = args
                forced_tool = "arxiv_search"
            elif cmd in ["/transcript", "/sub"]:
                command_instruction = f"Get the transcript for YouTube video ID: {args}. "
                clean_message = args
                forced_tool = "youtube_transcript"

        user_message_to_send = command_instruction + clean_message if command_instruction else user_message

        memory_context = get_memories(clean_message, user_id)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(memory=memory_context)

        async def _async_chat():
            # Build tool list directly — no subprocess, no MCP
            if enabled_tools is not None:
                tools = [
                    t for t in ALL_TOOLS
                    if t.name in enabled_tools or (forced_tool and t.name == forced_tool)
                ]
            else:
                tools = ALL_TOOLS

            tool_map = {t.name: t for t in tools}
            bound = _model_pool[_state["idx"]].bind_tools(tools) if tools else _model_pool[_state["idx"]]

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message_to_send),
            ]

            for _ in range(8):
                try:
                    ai_msg = await bound.ainvoke(messages)

                except Exception as exc:
                    if _is_rate_limit(exc):
                        next_idx = _state["idx"] + 1
                        if next_idx < len(_model_pool):
                            _state["idx"] = next_idx
                            next_model = _model_pool[next_idx]
                            bound = next_model.bind_tools(tools) if tools else next_model
                            print(f"Rate limit — switching to cascade model #{next_idx}: {MODEL_CASCADE[next_idx]}")
                            continue
                        raise

                    tool_name, t_args = _parse_malformed_call(str(exc))
                    if not tool_name:
                        raise

                    tool = tool_map.get(tool_name)
                    try:
                        result = await tool.ainvoke(t_args) if tool else f"Tool '{tool_name}' not available."
                    except Exception as te:
                        result = f"Tool error: {te}"

                    fake_id = "recovered_0"
                    messages.append(AIMessage(
                        content="",
                        tool_calls=[{
                            "name": tool_name,
                            "args": t_args,
                            "id": fake_id,
                            "type": "tool_call",
                        }],
                    ))
                    messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=fake_id,
                        name=tool_name,
                    ))
                    bound = _model_pool[_state["idx"]]
                    continue

                messages.append(ai_msg)

                tool_calls = getattr(ai_msg, "tool_calls", None) or []
                if not tool_calls:
                    break

                for tc in tool_calls:
                    tool = tool_map.get(tc["name"])
                    try:
                        result = await tool.ainvoke(tc["args"]) if tool else f"Unknown tool: {tc['name']}"
                    except Exception as te:
                        result = f"Tool error ({tc['name']}): {te}"
                    messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tc["id"],
                        name=tc["name"],
                    ))

            return messages

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            messages = loop.run_until_complete(_async_chat())
        finally:
            loop.close()

        last = messages[-1]
        if isinstance(last.content, list):
            reply = " ".join(
                p.get("text", "") if isinstance(p, dict) else str(p)
                for p in last.content
            ).strip()
        else:
            reply = last.content or "No response generated."

        github_data = None
        youtube_data = None
        for msg in messages:
            if not isinstance(msg, ToolMessage) or not msg.name:
                continue
            raw = msg.content if isinstance(msg.content, str) else str(msg.content)
            if msg.name == "github_search":
                try:
                    github_data = json.loads(raw)
                except Exception:
                    pass
            elif msg.name == "youtube_search":
                try:
                    youtube_data = json.loads(raw)
                except Exception:
                    pass

        try:
            import streamlit as st
            if github_data is not None:
                st.session_state.github_results = github_data
            if youtube_data is not None:
                st.session_state.youtube_results = youtube_data
        except Exception:
            pass

        add_memory(user_id, user_message, reply)

        return {
            "reply": reply,
            "github_results": github_data or [],
            "youtube_results": youtube_data or [],
        }

    except Exception as exc:
        msg = str(exc)
        if _is_rate_limit(exc):
            tried = ", ".join(MODEL_CASCADE[:_state["idx"] + 1])
            reply = (
                f"All {_state['idx'] + 1} model(s) in the cascade hit their rate limits ({tried}). "
                "Please wait a few minutes for quota to reset or upgrade at https://console.groq.com/settings/billing"
            )
        else:
            reply = f"Error: {msg}"
        return {
            "reply": reply,
            "github_results": [],
            "youtube_results": [],
        }
