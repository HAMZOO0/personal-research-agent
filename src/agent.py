import os
import sys
import json
import asyncio
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from src.config import SYSTEM_PROMPT_TEMPLATE
from src.memory import get_memories, add_memory

# Initialize LLM model
try:
    model = init_chat_model("groq:llama-3.3-70b-versatile")
    print("SUCCESS: Model initialized")
except Exception as e:
    model = None
    print(f"Model init error: {e}")


def chat(user_id: str, user_message: str, enabled_tools: list = None) -> dict:
    """Main chat function coordinate memory and agent loop."""
    if model is None:
        return {"reply": "Setup error: could not initialize model.", "github_results": [], "youtube_results": []}

    try:
        # Process slash commands and translate them into system instructions to force tools
        command_instruction = ""
        clean_message = user_message.strip()
        forced_tool = None
        
        if clean_message.startswith("/"):
            parts = clean_message.split(" ", 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if cmd in ["/websearch", "/search"]:
                command_instruction = f"[SYSTEM INSTRUCTION: Run the 'web_search' tool on query '{args}' and summarize findings.] "
                clean_message = args
                forced_tool = "web_search"
            elif cmd in ["/github", "/git"]:
                command_instruction = f"[SYSTEM INSTRUCTION: Run the 'github_search' tool on query '{args}' and list repositories.] "
                clean_message = args
                forced_tool = "github_search"
            elif cmd in ["/youtube", "/yt"]:
                command_instruction = f"[SYSTEM INSTRUCTION: Run the 'youtube_search' tool on query '{args}' and list/embed the videos.] "
                clean_message = args
                forced_tool = "youtube_search"
            elif cmd in ["/arxiv", "/paper"]:
                command_instruction = f"[SYSTEM INSTRUCTION: Run the 'fetch_arxiv_paper' tool on '{args}' and summarize it.] "
                clean_message = args
                forced_tool = "fetch_arxiv_paper"
            elif cmd in ["/transcript", "/sub"]:
                command_instruction = f"[SYSTEM INSTRUCTION: Run the 'youtube_transcript' tool on the video ID '{args}' to fetch and summarize its transcript.] "
                clean_message = args
                forced_tool = "youtube_transcript"

        user_message_to_send = command_instruction + clean_message if command_instruction else user_message

        # 1. Retrieve prior memories
        memory_context = get_memories(clean_message, user_id)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(memory=memory_context)

        # 2. Setup MCP Client with correct path as module runner
        python_path = sys.executable
        client = MultiServerMCPClient(
            {
                "research": {
                    "command": python_path,
                    "args": ["-m", "src.mcp_server"],
                    "transport": "stdio",
                }
            }
        )

        async def _async_chat():
            all_tools = await client.get_tools()
            if enabled_tools is not None:
                # Filter tools based on user options, but always allow the forced tool from slash command
                tools = [
                    t for t in all_tools 
                    if t.name in enabled_tools or (forced_tool and t.name == forced_tool)
                ]
            else:
                tools = all_tools
            
            agent_executor = create_react_agent(model, tools=tools, prompt=system_prompt)
            response = await agent_executor.ainvoke({"messages": [HumanMessage(content=user_message_to_send)]})
            return response

        # Run async agent in a dedicated event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(_async_chat())
        finally:
            loop.close()

        reply = response["messages"][-1].content

        # Parse and capture tool results for UI display
        github_data = None
        youtube_data = None
        for msg in response["messages"]:
            if hasattr(msg, "name") and msg.name:
                # Handle list/string content returned by MCP or other adapters
                content_str = ""
                if isinstance(msg.content, str):
                    content_str = msg.content
                elif isinstance(msg.content, list):
                    text_parts = []
                    for item in msg.content:
                        if isinstance(item, dict) and "text" in item:
                            text_parts.append(item["text"])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    content_str = "".join(text_parts)
                else:
                    content_str = str(msg.content)

                if msg.name == "github_search":
                    try:
                        github_data = json.loads(content_str)
                    except Exception:
                        pass
                elif msg.name == "youtube_search":
                    try:
                        youtube_data = json.loads(content_str)
                    except Exception:
                        pass

        # Save to streamlit session state if active
        try:
            import streamlit as st
            if github_data is not None:
                st.session_state.github_results = github_data
            if youtube_data is not None:
                st.session_state.youtube_results = youtube_data
        except Exception:
            pass

        # 3. Store new facts extracted from conversation
        add_memory(user_id, user_message, reply)

        return {
            "reply": reply,
            "github_results": github_data or [],
            "youtube_results": youtube_data or []
        }

    except Exception as exc:
        return {
            "reply": f"Error: {exc}",
            "github_results": [],
            "youtube_results": []
        }
