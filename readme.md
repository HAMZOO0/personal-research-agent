<div align="center">

# Personal Research Assistant

**An autonomous AI research agent with persistent semantic memory, multi-source tool orchestration, and a real-time Streamlit UI**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/LLM-Groq_5--Model_Cascade-F55036?style=flat-square&logo=groq&logoColor=white)](https://console.groq.com)
[![LangChain](https://img.shields.io/badge/Framework-LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Mem0](https://img.shields.io/badge/Memory-Mem0-6C63FF?style=flat-square)](https://mem0.ai)
[![FastMCP](https://img.shields.io/badge/Tools-FastMCP-00C7B7?style=flat-square)](https://github.com/jlowin/fastmcp)
[![Qdrant](https://img.shields.io/badge/VectorDB-Qdrant-DC244C?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)

*Ask questions, discover papers, search code, watch videos — all in one session, with memory that persists across conversations.*

</div>

---

## Overview

The Personal Research Assistant is a fully autonomous, agentic research system. It combines a multi-step reasoning loop with semantic long-term memory and a rich tool ecosystem spanning web search, arXiv, PubMed, YouTube, and GitHub. Each conversation is personalized to the user and builds on past research sessions, eliminating the need to repeat context.

**Core capabilities at a glance:**

| Capability | Description |
|---|---|
| Autonomous reasoning | LangChain ReAct loop decides which tools to call and in what order |
| Persistent memory | Mem0 stores and retrieves facts per user across sessions using vector search |
| Multi-source research | 8 tools: web, arXiv (search + PDF), PubMed, YouTube (search + transcript), GitHub |
| Slash command routing | `/papers`, `/git`, `/yt`, `/sub`, `/search`, `/paper` map directly to tools |
| 5-model cascade | Auto-advances through 5 Groq models on rate-limit — session never drops |
| MCP protocol support | All tools are also exposed as a FastMCP server for external integrations |

---

## System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    User(["👤 User"]):::user

    subgraph UI ["🖥️  Streamlit Frontend  (app.py)"]
        direction TB
        ChatInput["Chat Input\n+ Slash Commands"]
        ToolToggle["Tool Toggle Panel\n(+ popover)"]
        ResultRenderer["Result Renderer\n(Markdown · Cards · Embeds)"]
        SidebarMemory["Sidebar Memory Viewer"]
    end

    subgraph Core ["⚙️  Core Orchestration  (src/)"]
        direction TB
        Init["src/__init__.py\nPublic API: chat() · getAllMemory()"]
        Agent["src/agent.py\nReAct Loop · Tool Dispatch · Fallback Logic"]
        Config["src/config.py\nModel Config · MEM0_CONFIG · System Prompt"]
        Memory["src/memory.py\nMem0 Lifecycle: add · get · list"]
    end

    subgraph Tools ["🔧  Tool Layer  (src/tools/ + src/mcp_server.py)"]
        direction LR
        WebSearch["search.py\nDuckDuckGo"]
        ArxivSearch["arxiv.py\narXiv Search + PDF"]
        PubMed["pubmed.py\nNIH PubMed API"]
        YouTube["youtube.py\nSearch + Transcripts"]
        GitHub["github.py\nRepo Search"]
        MCP["mcp_server.py\nFastMCP Wrapper"]
    end

    subgraph External ["☁️  External Services"]
        Groq["Groq API\ngpt-oss-120b → qwen3.6-27b\n→ llama-3.3-70b → qwen3-32b → gpt-oss-20b"]
        Qdrant["Qdrant Vector Store"]
        HFEmbed["HuggingFace\nall-MiniLM-L6-v2 Embedder"]
        DDGS["DuckDuckGo\nDDGS"]
        ArxivAPI["arXiv.org\nSearch + PDF"]
        PubMedAPI["NCBI EUtils\nPubMed"]
        YTAPI["YouTube\nSearch + Transcripts"]
        GHAPI["GitHub API\nRepo Search"]
    end

    User -->|"query + user_id"| ChatInput
    User -->|"slash command"| ToolToggle
    ChatInput --> Init
    ToolToggle --> Init
    SidebarMemory -->|"getAllMemory()"| Init

    Init --> Agent
    Init --> Memory

    Agent -->|"get_memories()"| Memory
    Agent -->|"load prompts & model config"| Config
    Memory -->|"vector config"| Config

    Agent -->|"bind_tools() · ainvoke()"| Groq
    Agent --> WebSearch
    Agent --> ArxivSearch
    Agent --> PubMed
    Agent --> YouTube
    Agent --> GitHub

    Memory -->|"store / retrieve embeddings"| Qdrant
    Memory -->|"embed facts"| HFEmbed

    WebSearch -->|"DDGS.text()"| DDGS
    ArxivSearch -->|"search + PDF fetch"| ArxivAPI
    PubMed -->|"esearch · esummary · efetch"| PubMedAPI
    YouTube -->|"search + transcript"| YTAPI
    GitHub -->|"REST v3 API"| GHAPI

    MCP -.->|"wraps all tools\nfor external MCP clients"| WebSearch
    MCP -.-> ArxivSearch
    MCP -.-> YouTube
    MCP -.-> GitHub

    Agent -->|"reply + structured data"| Init
    Init --> ResultRenderer
    ResultRenderer --> User

    classDef user fill:#1a1a2e,stroke:#6C63FF,color:#e0e0e0
    classDef external fill:#0f3460,stroke:#16213e,color:#e0e0e0
```

---

### Request Lifecycle — Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit UI<br/>(app.py)
    participant Init as src/__init__.py
    participant Agent as Agent<br/>(agent.py)
    participant Memory as Memory<br/>(memory.py)
    participant Tools as Tool Layer<br/>(src/tools/)
    participant Groq as Groq LLM
    participant VDB as Qdrant<br/>Vector Store

    User->>UI: Submit query (text or /command)
    UI->>UI: Parse slash command → forced_tool + enabled_tools
    UI->>Init: chat(user_id, message, enabled_tools)
    Init->>Agent: Delegate to agent.chat()

    Agent->>Memory: get_memories(query, user_id)
    Memory->>VDB: semantic_search(embedding(query))
    VDB-->>Memory: Top-k relevant facts
    Memory-->>Agent: Formatted memory context

    Agent->>Agent: Build SystemMessage with<br/>SYSTEM_PROMPT_TEMPLATE + memory
    Agent->>Groq: bind_tools(active_tools).ainvoke(messages)

    loop ReAct Loop (max 8 iterations)
        Groq-->>Agent: AIMessage with tool_calls[]

        alt Tool calls present
            loop Each tool call
                Agent->>Tools: tool.ainvoke(args)
                Tools-->>Agent: ToolMessage(result)
            end
            Agent->>Groq: ainvoke(messages + tool results)
        else Rate limit / 429 hit
            Agent->>Agent: Increment cascade idx<br/>_state["idx"] + 1
            Agent->>Groq: Retry with next model in pool<br/>(up to 5 models)
        else Malformed tool call in error
            Agent->>Agent: _parse_malformed_call()<br/>Recover tool name + args
            Agent->>Tools: tool.ainvoke(recovered_args)
            Tools-->>Agent: ToolMessage(result)
        else No tool calls
            Agent->>Agent: Break loop — final reply ready
        end
    end

    Agent->>Memory: add_memory(user_id, message, reply)
    Memory->>VDB: upsert(embedding(facts))

    Agent-->>Init: {reply, github_results, youtube_results}
    Init-->>UI: Structured response dict
    UI->>UI: Render Markdown reply
    UI->>UI: Render GitHub / YouTube cards
    UI-->>User: Display final response + rich cards
```

---

### Agent ReAct Execution Loop — State Machine

```mermaid
stateDiagram-v2
    direction TB

    [*] --> ParseCommand : User sends query

    ParseCommand --> BuildContext : No slash command
    ParseCommand --> ForceToolBind : Slash command detected\n(/yt, /git, /paper, etc.)
    ForceToolBind --> BuildContext : forced_tool injected

    BuildContext --> FetchMemory : Retrieve user memories
    FetchMemory --> BuildPrompt : Inject memory into\nSYSTEM_PROMPT_TEMPLATE
    BuildPrompt --> BindTools : Filter active tools\nvia enabled_tools list

    BindTools --> InvokeGroq : model.bind_tools().ainvoke()

    InvokeGroq --> HasToolCalls : LLM response received
    HasToolCalls --> ExecuteTools : tool_calls present
    HasToolCalls --> FinalReply : No tool calls (done)

    ExecuteTools --> AppendResults : Await tool.ainvoke()
    AppendResults --> InvokeGroq : Feed results back to LLM

    InvokeGroq --> RateLimit : HTTP 429 / rate_limit_exceeded
    RateLimit --> SwitchFallback : More models in pool?
    SwitchFallback --> InvokeGroq : idx++ → bind next model\ngpt-oss-120b→qwen3.6-27b→llama-3.3-70b→qwen3-32b→gpt-oss-20b
    SwitchFallback --> ErrorState : All 5 models exhausted

    InvokeGroq --> MalformedCall : Tool call parse error
    MalformedCall --> RecoverCall : _parse_malformed_call()
    RecoverCall --> ExecuteTools : Recovered name + args
    RecoverCall --> ErrorState : Cannot recover

    FinalReply --> PersistMemory : add_memory(user_id, ...)
    PersistMemory --> ExtractCards : Parse YouTube / GitHub\ntool results from messages
    ExtractCards --> ReturnResponse : {reply, github, youtube}

    ErrorState --> ReturnError : Friendly error message
    ReturnResponse --> [*]
    ReturnError --> [*]
```

---

### Model Cascade — Automatic Rate-Limit Recovery

```mermaid
flowchart LR
    Start(["🚀 Request\nStarts"])

    subgraph Cascade ["MODEL_CASCADE  —  Tried left → right on every 429"]
        M1["1️⃣  openai/gpt-oss-120b\nStrongest reasoning\nBest for agents + tool use"]
        M2["2️⃣  qwen/qwen3.6-27b\nCoding specialist\n262K context window"]
        M3["3️⃣  llama-3.3-70b-versatile\nReliable all-rounder\nStrong RAG"]
        M4["4️⃣  qwen/qwen3-32b\nSolid coding + RAG\nGood context"]
        M5["5️⃣  openai/gpt-oss-20b\nFastest · Lightest\nLast resort"]
    end

    RateLimit{{"⚡ 429 /\nrate_limit_exceeded"}}
    Exhausted["❌ All models exhausted\nShow user error + billing link"]
    Reply(["✅ Reply\nReturned"])

    Start --> M1
    M1 -->|"Success"| Reply
    M1 -->|"Rate limit"| RateLimit
    RateLimit -->|"idx=1"| M2
    M2 -->|"Success"| Reply
    M2 -->|"Rate limit"| RateLimit
    RateLimit -->|"idx=2"| M3
    M3 -->|"Success"| Reply
    M3 -->|"Rate limit"| RateLimit
    RateLimit -->|"idx=3"| M4
    M4 -->|"Success"| Reply
    M4 -->|"Rate limit"| RateLimit
    RateLimit -->|"idx=4"| M5
    M5 -->|"Success"| Reply
    M5 -->|"Rate limit"| Exhausted
```

> All 5 models are initialized at startup into `_model_pool`. Switching happens **mid-loop** — the conversation, tool results, and message history are preserved across the switch.

---

### Memory System Architecture

```mermaid
flowchart LR
    subgraph Input ["Input Layer"]
        Query["User Query"]
        Reply["Agent Reply"]
        UID["User ID"]
    end

    subgraph Mem0 ["Mem0 Memory Engine  (src/memory.py)"]
        direction TB
        AddMem["add_memory()\nExtract facts from conversation"]
        GetMem["get_memories()\nSemantic retrieval by query"]
        ListMem["list_all()\nFull history dump"]
        LLMExtract["Groq (active cascade model)\nFact extraction & summarization"]
    end

    subgraph VectorPipeline ["Vector Pipeline"]
        direction TB
        Embedder["HuggingFace Embedder\nall-MiniLM-L6-v2\n384 dims"]
        QdrantMem["Qdrant Vector Store\ncollection: mem0_research_assistant"]
        TopK["Top-K Semantic Search\nk=5 relevant facts"]
    end

    subgraph Output ["Context Output"]
        MemCtx["Formatted Memory Context\nInjected into System Prompt"]
    end

    Query -->|"new query"| GetMem
    Reply -->|"conversation turn"| AddMem
    UID -->|"per-user partition"| AddMem
    UID -->|"per-user filter"| GetMem

    AddMem -->|"extract facts"| LLMExtract
    LLMExtract -->|"embed"| Embedder
    Embedder -->|"upsert vectors"| QdrantMem

    GetMem -->|"embed query"| Embedder
    Embedder -->|"ANN search"| QdrantMem
    QdrantMem -->|"k nearest facts"| TopK
    TopK --> MemCtx

    ListMem -->|"scroll all"| QdrantMem
```

---

### Tool Ecosystem Map

```mermaid
flowchart LR
    Agent(["🤖 Agent\nReAct Loop"])

    subgraph WebTools ["Web Intelligence"]
        WS["🌐 web_search\nDuckDuckGo DDGS\n6 results per query"]
    end

    subgraph AcademicTools ["Academic Research"]
        AS["📄 arxiv_search\nSearch by topic\nReturns IDs + abstracts"]
        AF["📑 fetch_arxiv_paper\nDownload + parse full PDF\nby arXiv ID or URL"]
        PM["🔬 pubmed_search\nNIH EUtils API\nesearch + esummary + efetch"]
    end

    subgraph MediaTools ["Media & Code"]
        YS["▶️ youtube_search\nVideo titles + IDs + URLs"]
        YT["📝 youtube_transcript\nFull transcript by video ID"]
        GH["💻 github_search\nRepo name + stars + desc + URL"]
    end

    subgraph MCPLayer ["MCP Protocol Layer"]
        MCP["⚡ FastMCP Server\nsrc/mcp_server.py\nstdio transport"]
    end

    Agent -->|"bind + invoke"| WS
    Agent --> AS
    Agent --> AF
    Agent --> PM
    Agent --> YS
    Agent --> YT
    Agent --> GH

    MCP -.->|"wraps"| WS
    MCP -.-> AS
    MCP -.-> AF
    MCP -.-> YS
    MCP -.-> YT
    MCP -.-> GH

    WS -->|"DDGS.text()"| DDG[("DuckDuckGo")]
    AS -->|"GET /search"| AX[("arXiv.org")]
    AF -->|"GET /pdf/ID"| AX
    PM -->|"esearch · esummary · efetch"| NCBI[("NCBI EUtils")]
    YS -->|"scrape / yt-dlp"| YTube[("YouTube")]
    YT -->|"YouTubeTranscriptApi"| YTube
    GH -->|"GitHub REST v3"| GHub[("GitHub API")]
```

---

### Slash Command → Tool Routing

```mermaid
flowchart TD
    Input(["User Input"])

    Input --> IsSlash{Starts with /\n?}

    IsSlash -->|No| DirectChat["Natural language query\nAgent picks tools via ReAct reasoning"]

    IsSlash -->|Yes| ParseCmd["Parse command + args"]

    ParseCmd --> CmdMap{Command}

    CmdMap -->|"/search or /websearch"| WSTool["🌐 web_search(args)"]
    CmdMap -->|"/papers or /asearch"| ASTool["📄 arxiv_search(args)"]
    CmdMap -->|"/paper or /arxiv"| AFTool["📑 fetch_arxiv_paper(args)"]
    CmdMap -->|"/git or /github"| GHTool["💻 github_search(args)"]
    CmdMap -->|"/yt or /youtube"| YSTool["▶️ youtube_search(args)"]
    CmdMap -->|"/sub or /transcript"| YTTool["📝 youtube_transcript(args)"]

    WSTool --> AgentLoop(["Agent ReAct Loop\nforced_tool bound first"])
    ASTool --> AgentLoop
    AFTool --> AgentLoop
    GHTool --> AgentLoop
    YSTool --> AgentLoop
    YTTool --> AgentLoop
    DirectChat --> AgentLoop

    AgentLoop --> Reply(["Structured Response\n{reply · github_results · youtube_results}"])
```

---

## Directory Structure

```
Personal research assistant/
│
├── app.py                          # Streamlit dashboard entry point
├── requirements.txt                # Project dependencies
├── .env                            # API keys (not committed)
├── .gitignore
├── README.md
│
├── public/
│   └── arct.png                    # Architecture diagram image
│
├── src/                            # Core application package
│   ├── __init__.py                 # Public API: chat(), getAllMemory()
│   ├── config.py                   # MEM0_CONFIG, model IDs, SYSTEM_PROMPT_TEMPLATE
│   ├── agent.py                    # ReAct loop, tool binding, fallback, slash routing
│   ├── memory.py                   # Mem0 wrapper: add_memory(), get_memories()
│   ├── mcp_server.py               # FastMCP server exposing all tools over stdio
│   │
│   └── tools/                      # Modular tool implementations
│       ├── __init__.py
│       ├── search.py               # DuckDuckGo web search (DDGS)
│       ├── arxiv.py                # arXiv keyword search + full PDF extraction
│       ├── pubmed.py               # PubMed search via NIH EUtils API
│       ├── youtube.py              # YouTube search + transcript fetching
│       └── github.py               # GitHub repository search
│
└── tests/                          # Test suite
    ├── __init__.py
    ├── test_agent.py               # End-to-end agent + tool-call test
    ├── test_imports.py             # Dependency import verification
    └── test_memory.py              # Mem0 initialization + embedding test
```

---

## Features

### Autonomous Multi-Step Research
The LangChain ReAct agent loop reasons over tool results iteratively. A single query like *"explain graph RAG"* triggers: `web_search` → `arxiv_search` → `fetch_arxiv_paper` (×2–3) → synthesized answer with full citations — with no manual intervention.

### Semantic Long-Term Memory
Mem0 extracts facts from each conversation turn and stores them as dense vectors in Qdrant. On the next session, the top-5 most relevant memories are retrieved and injected into the system prompt, giving the assistant context about past research without re-stating it.

### PubMed Integration
Peer-reviewed biomedical papers from NCBI PubMed are accessible via the three-stage EUtils pipeline: `esearch` (discover PMIDs) → `esummary` (metadata) → `efetch` (full abstracts). Ideal for clinical and life-science research queries.

### arXiv Full-Text Reading
Instead of relying on short descriptions, `fetch_arxiv_paper` downloads the actual PDF and extracts its text so the LLM reasons over full methodology sections, not just titles.

### YouTube Intelligence
Search for tutorial videos on any topic and extract full transcripts for summarization — useful for understanding talks, lectures, and demos without watching them.

### GitHub Code Discovery
Search repositories by topic, returning name, stars, description, and URL rendered as interactive cards in the UI.

### 5-Model Cascade — Zero-Drop Rate-Limit Recovery
All five Groq models are initialized at startup into a pool. When any model returns a `429 / rate_limit_exceeded`, the agent increments the cascade index and rebinds the next model **mid-loop** — preserving the full message history, tool results, and conversation state. The cascade order is:

| Priority | Model ID | Strength |
|---|---|---|
| 1 (Primary) | `openai/gpt-oss-120b` | Strongest reasoning, best tool use |
| 2 | `qwen/qwen3.6-27b` | Coding specialist, 262K context |
| 3 | `llama-3.3-70b-versatile` | Reliable all-rounder |
| 4 | `qwen/qwen3-32b` | Solid RAG + coding |
| 5 (Last resort) | `openai/gpt-oss-20b` | Fastest, lightest |

If all 5 are exhausted the user sees a single message listing exactly which models were tried.

### Malformed Tool Call Recovery
A regex-based parser recovers tool calls that arrive as raw text instead of structured JSON (a known behavior in some Groq model responses), preventing silent failures.

### FastMCP Protocol Layer
All tools are exposed as a FastMCP server (`src/mcp_server.py`) over stdio, making the tool ecosystem compatible with any MCP-capable client or orchestrator.

### Per-User Isolation
Every memory operation is scoped to a `user_id`, enabling true multi-tenant behavior where different users maintain completely separate research histories.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| LLM #1 (Primary) | Groq `openai/gpt-oss-120b` | Strongest reasoning + tool calling |
| LLM #2 | Groq `qwen/qwen3.6-27b` | Coding + long-context RAG |
| LLM #3 | Groq `llama-3.3-70b-versatile` | All-rounder |
| LLM #4 | Groq `qwen/qwen3-32b` | Solid coding + RAG fallback |
| LLM #5 (Last resort) | Groq `openai/gpt-oss-20b` | Fastest, lightest |
| Agent Framework | LangChain (`init_chat_model`, `bind_tools`) | ReAct loop and tool dispatch |
| Memory Engine | Mem0 | Fact extraction, storage, and retrieval |
| Vector Database | Qdrant | Dense vector storage for memories |
| Embedder | HuggingFace `all-MiniLM-L6-v2` | 384-dim sentence embeddings |
| MCP Layer | FastMCP | Tool protocol server |
| UI | Streamlit | Chat interface and rich card rendering |
| Web Search | DuckDuckGo DDGS | Scrape-free web results |
| Academic | arXiv API + PDF | Paper discovery and full-text reading |
| Biomedical | NCBI EUtils (PubMed) | Peer-reviewed medical literature |
| Media | YouTube Transcript API | Video search and transcript extraction |
| Code Discovery | GitHub REST v3 | Repository search |

---

## Setup & Installation

**1. Clone the repository**
```bash
git clone <repository-url>
cd "Personal research assistant"
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Running the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

**Using the MCP server standalone:**
```bash
python -m src.mcp_server
```

---

## Slash Commands Reference

| Command | Alias | Description | Bound Tool |
|---|---|---|---|
| `/search <query>` | `/websearch` | Search the web | `web_search` |
| `/papers <topic>` | `/asearch` | Find arXiv papers | `arxiv_search` |
| `/paper <id>` | `/arxiv` | Read full arXiv paper | `fetch_arxiv_paper` |
| `/git <query>` | `/github` | Search GitHub repos | `github_search` |
| `/yt <query>` | `/youtube` | Find YouTube videos | `youtube_search` |
| `/sub <video_id>` | `/transcript` | Get video transcript | `youtube_transcript` |

Without a slash command, the agent autonomously decides which tools to invoke based on your query.

---

## Testing

**Verify memory initialization:**
```bash
python -m tests.test_memory
```
Expected: `SUCCESS: Memory initialized successfully!`

**Verify module imports:**
```bash
python -m tests.test_imports
```
Expected: Success notifications for all LangChain and LangGraph imports.

**Verify agent and tool calling (end-to-end):**
```bash
python -m tests.test_agent
```
Expected: Agent downloads, reads, and summarizes an arXiv paper with citations.

---

## License

This project is provided for educational and personal research use.
