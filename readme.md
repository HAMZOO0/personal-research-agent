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

## Table of Contents

| # | Section |
|---|---|
| 1 | [Overview](#overview) |
| 2 | [Screenshots](#screenshots) |
| 3 | [Key Features](#key-features) |
| 4 | [Architecture](#architecture) |
| 5 | [How It Works](#how-it-works) |
| 6 | [Tech Stack](#tech-stack) |
| 7 | [Project Structure](#project-structure) |
| 8 | [Getting Started](#getting-started) |
| 9 | [Configuration](#configuration) |
| 10 | [Usage](#usage) |
| 11 | [Demo Knowledge Base](#demo-knowledge-base) |
| 12 | [Test Scenarios](#test-scenarios) |
| 13 | [Roadmap](#roadmap) |

---

## Overview

The Personal Research Assistant is a fully autonomous, agentic research system. It combines a multi-step reasoning loop with semantic long-term memory and a rich tool ecosystem spanning web search, arXiv, PubMed, YouTube, and GitHub. Each conversation is personalized to the user and builds on past research sessions — eliminating the need to repeat context.

The system is built for researchers, developers, and students who need to synthesize information from multiple sources quickly. A single natural-language query triggers a chain of tool calls — web search, paper discovery, full PDF reading, video search — and returns a single structured, cited answer.

**Core capabilities at a glance:**

| Capability | Description |
|---|---|
| Autonomous reasoning | LangChain ReAct loop decides which tools to call and in what order |
| Persistent memory | Mem0 stores and retrieves facts per user across sessions using vector search |
| Multi-source research | 7 tools: web, arXiv (search + PDF), PubMed, YouTube (search + transcript), GitHub |
| Slash command routing | `/papers`, `/pubmed`, `/git`, `/yt`, `/sub`, `/search`, `/paper` map directly to tools |
| 5-model cascade | Auto-advances through 5 Groq models on rate-limit — session never drops |
| Live model indicator | Sidebar + per-reply badge shows exactly which model handled each response |
| MCP protocol support | All tools exposed as a FastMCP server for external client integrations |

---

## Screenshots

### System Architecture Diagram

<div align="center">
  <img src="public/system design.jpeg" width="100%" alt="Personal Research Assistant — System Architecture" />
</div>

---

### Dashboard — Main Chat Interface

<div align="center">
  <img src="public/Screenshot_29-6-2026_11477_localhost.jpeg" width="100%" alt="Main chat interface with Active Model indicator and sidebar" />
</div>

---

### Research Output — Detailed Analysis

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <img src="public/Screenshot_29-6-2026_114722_localhost.jpeg" width="100%" alt="Detailed clinical analysis with study citations" />
        <br/><sub>Clinical efficacy analysis with inline citations</sub>
      </td>
      <td align="center" width="50%">
        <img src="public/Screenshot_29-6-2026_114727_localhost.jpeg" width="100%" alt="Mechanism of action table" />
        <br/><sub>Mechanistic breakdown rendered as a table</sub>
      </td>
    </tr>
  </table>
</div>

---

### Research Papers — PubMed Results

<div align="center">
  <img src="public/Screenshot_29-6-2026_114737_localhost.jpeg" width="100%" alt="PubMed research papers table with PMID, authors, abstracts, and key findings" />
  <br/><sub>PubMed results — full citation table with PMID, authors, abstracts, key findings, and PDF links</sub>
</div>

---

### Web Sources & YouTube Citations

<div align="center">
  <img src="public/Screenshot_29-6-2026_114747_localhost.jpeg" width="100%" alt="Web sources and YouTube videos citation tables" />
  <br/><sub>Structured web sources and YouTube video citations with channel and main focus</sub>
</div>

---

### YouTube Insights — Compact Video Cards

<div align="center">
  <img src="public/youtub.jpeg" width="100%" alt="YouTube compact video cards with thumbnails" />
  <br/><sub>Compact YouTube cards — thumbnail, title, and Watch link side-by-side</sub>
</div>

---

### Tool Toggle Panel & Slash Commands

<div align="center">
  <img src="public/slah tools and skill.jpeg" width="100%" alt="Tool toggle panel showing all 6 active skills and slash commands reference" />
  <br/><sub>Tool toggle panel — enable/disable individual tools per query and slash command reference</sub>
</div>

---

### YouTube Transcript Analysis via /yt Command

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <img src="public/Screenshot_29-6-2026_115421_localhost.jpeg" width="100%" alt="YouTube command response with video table" />
        <br/><sub>/yt command — video table with channel, length, and main focus</sub>
      </td>
      <td align="center" width="50%">
        <img src="public/Screenshot_29-6-2026_115427_localhost.jpeg" width="100%" alt="YouTube detailed video analysis" />
        <br/><sub>Themes analysis across multiple videos</sub>
      </td>
    </tr>
  </table>
</div>

---

## Key Features

### Autonomous Multi-Step Research
The LangChain ReAct loop reasons over tool results iteratively. A single query like *"explain graph RAG"* triggers `web_search` → `arxiv_search` → `fetch_arxiv_paper` (×2–3) → synthesized answer with full citations, with zero manual intervention.

### Smart Paper Database Routing
The system prompt intelligently routes paper searches to the correct database:
- **Medical / clinical / pharmacology / biology** → `pubmed_search` (NCBI PubMed)
- **AI / ML / computer science / physics / math** → `arxiv_search` (arXiv.org)

This prevents the classic mistake of searching arXiv for medical topics and getting physics papers with matching words (e.g. searching "hair loss" and getting *black hole hair* papers).

### Semantic Long-Term Memory
Mem0 extracts facts from each conversation turn and stores them as dense vectors in Qdrant. On the next session, the top-5 most relevant memories are retrieved and injected into the system prompt — the assistant knows what you've already researched.

### 5-Model Cascade — Zero-Drop Rate-Limit Recovery
All five Groq models are initialized at startup. When any model returns a `429`, the agent increments the cascade index and rebinds the next model **mid-loop** — preserving full message history, tool results, and conversation state across the switch.

| Priority | Model | Strength |
|---|---|---|
| 1 (Primary) | `openai/gpt-oss-120b` | Strongest reasoning, best tool use |
| 2 | `qwen/qwen3.6-27b` | Coding specialist, 262K context |
| 3 | `llama-3.3-70b-versatile` | Reliable all-rounder |
| 4 | `qwen/qwen3-32b` | Solid RAG + coding |
| 5 (Last resort) | `openai/gpt-oss-20b` | Fastest, lightest |

### Live Model Indicator
A glowing colored dot in the sidebar and a small badge under every reply shows exactly which model answered — color-coded per model, updates in real time.

### PubMed Full-Pipeline Integration
Three-stage NCBI EUtils pipeline: `esearch` (discover PMIDs) → `esummary` (metadata: title, authors, journal, date) → `efetch` (full abstract text). Returns properly formatted citations with PubMed URLs.

### arXiv Full-Text PDF Reading
`fetch_arxiv_paper` downloads the actual PDF and extracts its full text — the LLM reasons over methodology sections, results, and conclusions, not just the abstract title.

### YouTube Intelligence
Search for tutorial videos on any topic and extract full transcripts for summarization — useful for understanding talks, lectures, and demos without watching them.

### GitHub Code Discovery
Search repositories by topic returning name, stars, description, and URL — rendered as interactive dark-theme cards in the UI.

### Malformed Tool Call Recovery
A regex-based parser recovers tool calls that arrive as raw text instead of structured JSON (a known edge case in some Groq model responses), preventing silent failures.

### FastMCP Protocol Layer
All tools are exposed as a FastMCP server (`src/mcp_server.py`) over stdio — compatible with any MCP-capable client or orchestrator.

### Per-User Isolation
Every memory operation is scoped to a `user_id`, enabling true multi-tenant behavior where each user has a completely separate research history.

---

## Architecture

### High-Level Architecture

```mermaid
flowchart TB
    User(["User"]):::user

    subgraph UI ["Streamlit Frontend  (app.py)"]
        direction TB
        ChatInput["Chat Input\n+ Slash Commands"]
        ToolToggle["Tool Toggle Panel\n(+ popover)"]
        ResultRenderer["Result Renderer\n(Markdown · Cards · Embeds)"]
        SidebarMemory["Sidebar Memory Viewer\n+ Active Model Indicator"]
    end

    subgraph Core ["Core Orchestration  (src/)"]
        direction TB
        Init["src/__init__.py\nPublic API: chat() · getAllMemory()"]
        Agent["src/agent.py\nReAct Loop · Tool Dispatch · Cascade Logic"]
        Config["src/config.py\nMODEL_CASCADE · MEM0_CONFIG · System Prompt"]
        Memory["src/memory.py\nMem0 Lifecycle: add · get · list"]
    end

    subgraph Tools ["Tool Layer  (src/tools/ + src/mcp_server.py)"]
        direction LR
        WebSearch["search.py\nDuckDuckGo"]
        ArxivSearch["arxiv.py\narXiv Search + PDF"]
        PubMed["pubmed.py\nNIH PubMed API"]
        YouTube["youtube.py\nSearch + Transcripts"]
        GitHub["github.py\nRepo Search"]
        MCP["mcp_server.py\nFastMCP Wrapper"]
    end

    subgraph External ["External Services"]
        Groq["Groq API\ngpt-oss-120b → qwen3.6-27b\n→ llama-3.3-70b → qwen3-32b → gpt-oss-20b"]
        Qdrant["Qdrant Vector Store"]
        HFEmbed["HuggingFace\nall-MiniLM-L6-v2 Embedder"]
        DDGS["DuckDuckGo DDGS"]
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
    Agent -->|"load prompts & cascade"| Config
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
    MCP -.-> PubMed
    MCP -.-> YouTube
    MCP -.-> GitHub

    Agent -->|"reply + model_used + cards"| Init
    Init --> ResultRenderer
    ResultRenderer --> User

    classDef user fill:#1a1a2e,stroke:#6C63FF,color:#e0e0e0
```

---

### Request Lifecycle — Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit UI (app.py)
    participant Init as src/__init__.py
    participant Agent as Agent (agent.py)
    participant Memory as Memory (memory.py)
    participant Tools as Tool Layer (src/tools/)
    participant Groq as Groq LLM cascade
    participant VDB as Qdrant Vector Store

    User->>UI: Submit query (text or /command)
    UI->>UI: Parse slash command → forced_tool + enabled_tools
    UI->>Init: chat(user_id, message, enabled_tools)
    Init->>Agent: Delegate to agent.chat()

    Agent->>Memory: get_memories(query, user_id)
    Memory->>VDB: semantic_search(embedding(query))
    VDB-->>Memory: Top-k relevant facts
    Memory-->>Agent: Formatted memory context

    Agent->>Agent: Build SystemMessage with SYSTEM_PROMPT_TEMPLATE + memory
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
            Agent->>Agent: Increment cascade idx
            Agent->>Groq: Retry with next model in pool (up to 5)
        else Malformed tool call in error
            Agent->>Agent: _parse_malformed_call() — recover name + args
            Agent->>Tools: tool.ainvoke(recovered_args)
            Tools-->>Agent: ToolMessage(result)
        else No tool calls
            Agent->>Agent: Break loop — final reply ready
        end
    end

    Agent->>Memory: add_memory(user_id, message, reply)
    Memory->>VDB: upsert(embedding(facts))

    Agent-->>Init: reply + github_results + youtube_results + model_used
    Init-->>UI: Structured response dict
    UI->>UI: Render Markdown reply + model badge
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
    ParseCommand --> ForceToolBind : Slash command detected (/yt, /git, /paper, /pubmed etc.)
    ForceToolBind --> BuildContext : forced_tool injected

    BuildContext --> FetchMemory : Retrieve user memories
    FetchMemory --> BuildPrompt : Inject memory into SYSTEM_PROMPT_TEMPLATE
    BuildPrompt --> BindTools : Filter active tools via enabled_tools list

    BindTools --> InvokeGroq : model.bind_tools().ainvoke()

    InvokeGroq --> HasToolCalls : LLM response received
    HasToolCalls --> ExecuteTools : tool_calls present
    HasToolCalls --> FinalReply : No tool calls (done)

    ExecuteTools --> AppendResults : Await tool.ainvoke()
    AppendResults --> InvokeGroq : Feed results back to LLM

    InvokeGroq --> RateLimit : HTTP 429 / rate_limit_exceeded
    RateLimit --> SwitchFallback : More models in pool?
    SwitchFallback --> InvokeGroq : idx++ bind next model
    SwitchFallback --> ErrorState : All 5 models exhausted

    InvokeGroq --> MalformedCall : Tool call parse error
    MalformedCall --> RecoverCall : _parse_malformed_call()
    RecoverCall --> ExecuteTools : Recovered name + args
    RecoverCall --> ErrorState : Cannot recover

    FinalReply --> PersistMemory : add_memory(user_id, ...)
    PersistMemory --> ExtractCards : Parse YouTube / GitHub tool results
    ExtractCards --> ReturnResponse : reply + github + youtube + model_used

    ErrorState --> ReturnError : Friendly error message
    ReturnResponse --> [*]
    ReturnError --> [*]
```

---

### Model Cascade — Automatic Rate-Limit Recovery

```mermaid
flowchart LR
    Start(["Request\nStarts"])

    subgraph Cascade ["MODEL_CASCADE  —  Tried left to right on every 429"]
        M1["1. openai/gpt-oss-120b\nStrongest reasoning\nBest for agents + tool use"]
        M2["2. qwen/qwen3.6-27b\nCoding specialist\n262K context window"]
        M3["3. llama-3.3-70b-versatile\nReliable all-rounder\nStrong RAG"]
        M4["4. qwen/qwen3-32b\nSolid coding + RAG\nGood context"]
        M5["5. openai/gpt-oss-20b\nFastest and Lightest\nLast resort"]
    end

    RateLimit{{"429 / rate_limit_exceeded"}}
    Exhausted["All models exhausted\nShow user error + billing link"]
    Reply(["Reply + model_used\nReturned"])

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

> All 5 models are initialized at startup into `_model_pool`. Switching happens **mid-loop** — the conversation, tool results, and message history are fully preserved across every switch.

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
        ListMem["getAllMemory()\nFull history dump"]
        LLMExtract["Groq (active cascade model)\nFact extraction and summarization"]
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
    Agent(["Agent\nReAct Loop"])

    subgraph WebTools ["Web Intelligence"]
        WS["web_search\nDuckDuckGo DDGS\n6 results per query"]
    end

    subgraph AcademicTools ["Academic Research"]
        AS["arxiv_search\nCS · AI · Physics · Math\nReturns IDs + abstracts"]
        AF["fetch_arxiv_paper\nDownload + parse full PDF\nby arXiv ID or URL"]
        PM["pubmed_search\nMedical · Clinical · Biology\nesearch + esummary + efetch"]
    end

    subgraph MediaTools ["Media and Code"]
        YS["youtube_search\nVideo titles + IDs + URLs"]
        YT["youtube_transcript\nFull transcript by video ID"]
        GH["github_search\nRepo name + stars + desc + URL"]
    end

    subgraph MCPLayer ["MCP Protocol Layer"]
        MCP["FastMCP Server\nsrc/mcp_server.py\nstdio transport"]
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
    MCP -.-> PM
    MCP -.-> YS
    MCP -.-> YT
    MCP -.-> GH

    WS -->|"DDGS.text()"| DDG[("DuckDuckGo")]
    AS -->|"GET /search"| AX[("arXiv.org")]
    AF -->|"GET /pdf/ID"| AX
    PM -->|"esearch · esummary · efetch"| NCBI[("NCBI EUtils")]
    YS -->|"scrape"| YTube[("YouTube")]
    YT -->|"YouTubeTranscriptApi"| YTube
    GH -->|"GitHub REST v3"| GHub[("GitHub API")]
```

---

### Slash Command Routing

```mermaid
flowchart TD
    Input(["User Input"])
    Input --> IsSlash{Starts with /}
    IsSlash -->|No| DirectChat["Natural language query\nAgent picks tools via ReAct reasoning"]
    IsSlash -->|Yes| ParseCmd["Parse command + args"]
    ParseCmd --> CmdMap{Command}
    CmdMap -->|"/search or /websearch"| WSTool["web_search(args)"]
    CmdMap -->|"/papers or /asearch"| ASTool["arxiv_search(args)"]
    CmdMap -->|"/paper or /arxiv"| AFTool["fetch_arxiv_paper(args)"]
    CmdMap -->|"/pubmed or /med"| PMTool["pubmed_search(args)"]
    CmdMap -->|"/git or /github"| GHTool["github_search(args)"]
    CmdMap -->|"/yt or /youtube"| YSTool["youtube_search(args)"]
    CmdMap -->|"/sub or /transcript"| YTTool["youtube_transcript(args)"]
    WSTool --> AgentLoop(["Agent ReAct Loop\nforced_tool bound first"])
    ASTool --> AgentLoop
    AFTool --> AgentLoop
    PMTool --> AgentLoop
    GHTool --> AgentLoop
    YSTool --> AgentLoop
    YTTool --> AgentLoop
    DirectChat --> AgentLoop
    AgentLoop --> Reply(["Structured Response\nreply · github_results · youtube_results · model_used"])
```

---

## How It Works

**Step 1 — Input parsing**
The user types a query or uses a slash command like `/pubmed minoxidil hair loss`. `app.py` detects the prefix, sets `forced_tool = "pubmed_search"`, and calls `chat(user_id, message, enabled_tools)`.

**Step 2 — Memory retrieval**
`agent.chat()` calls `get_memories(query, user_id)` which embeds the query using `all-MiniLM-L6-v2` and runs ANN search against Qdrant. The top-5 semantically relevant facts from past sessions are returned and formatted into the system prompt.

**Step 3 — Model selection**
The agent picks the first available model from `MODEL_CASCADE` (starting at index 0: `openai/gpt-oss-120b`), binds the active tool set with `model.bind_tools(tools)`, and invokes the LLM.

**Step 4 — ReAct reasoning loop (max 8 iterations)**
The LLM returns an `AIMessage`. If it contains `tool_calls`, the agent executes each tool, appends `ToolMessage` results, and re-invokes the LLM. This continues until the model returns a reply with no tool calls. On a `429`, the cascade index increments and the next model takes over without losing state.

**Step 5 — Tool database routing**
The system prompt instructs the model: medical queries → `pubmed_search`, CS/AI queries → `arxiv_search`. For arXiv results, the agent also calls `fetch_arxiv_paper` to read the full PDF of the top 2–3 papers.

**Step 6 — Memory persistence**
After the final reply, `add_memory(user_id, message, reply)` extracts key facts from the conversation and upserts them as embeddings into Qdrant under the user's partition.

**Step 7 — Response rendering**
The structured dict `{reply, github_results, youtube_results, model_used}` is returned to `app.py`. The reply renders as markdown, GitHub repos as dark-theme cards with star counts, YouTube videos as compact thumbnail cards. The active model badge updates in the sidebar and below the reply.

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
| Vector Database | Qdrant (`./qdrant_store`) | Persistent dense vector storage |
| Embedder | HuggingFace `all-MiniLM-L6-v2` | 384-dim sentence embeddings |
| MCP Layer | FastMCP | Tool protocol server (stdio transport) |
| UI | Streamlit | Chat interface and rich card rendering |
| Web Search | DuckDuckGo DDGS | Scrape-free web results (6 per query) |
| CS/AI Papers | arXiv API + PDF | Paper discovery and full-text reading |
| Medical Papers | NCBI EUtils (PubMed) | Peer-reviewed biomedical literature |
| Video | YouTube Transcript API | Video search and transcript extraction |
| Code | GitHub REST v3 | Repository search |
| Environment | python-dotenv | API key management |

---

## Project Structure

```
Personal research assistant/
│
├── app.py                          # Streamlit dashboard — entry point
├── requirements.txt                # All Python dependencies
├── .env                            # Secret keys (not committed)
├── .gitignore
├── README.md
│
├── public/                         # Screenshots and architecture diagrams
│   ├── system design.jpeg          # Full system architecture (Eraser.io)
│   ├── slah tools and skill.jpeg   # Tool toggle panel screenshot
│   ├── youtub.jpeg                 # YouTube compact cards screenshot
│   └── Screenshot_*.jpeg           # Dashboard and output screenshots
│
├── qdrant_store/                   # Persistent vector DB (auto-created, git-ignored)
│
├── src/                            # Core application package
│   ├── __init__.py                 # Public API: chat(), getAllMemory()
│   ├── config.py                   # MODEL_CASCADE, MEM0_CONFIG, SYSTEM_PROMPT_TEMPLATE
│   ├── agent.py                    # ReAct loop, tool binding, cascade, slash routing
│   ├── memory.py                   # Mem0 wrapper: add_memory(), get_memories(), getAllMemory()
│   ├── mcp_server.py               # FastMCP server exposing all 7 tools over stdio
│   │
│   └── tools/                      # Modular tool implementations
│       ├── __init__.py
│       ├── search.py               # DuckDuckGo DDGS web search
│       ├── arxiv.py                # arXiv keyword search + full PDF text extraction
│       ├── pubmed.py               # PubMed search via NCBI EUtils (esearch/esummary/efetch)
│       ├── youtube.py              # YouTube search + transcript fetching
│       └── github.py              # GitHub repository search (REST v3)
│
└── tests/                          # Test suite
    ├── __init__.py
    ├── test_agent.py               # End-to-end agent + tool-call test
    ├── test_imports.py             # Dependency import verification
    └── test_memory.py              # Mem0 initialization + embedding test
```

---

## Getting Started

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

**4. Add your API key** (see [Configuration](#configuration))

**5. Run the app**
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### Model Cascade (`src/config.py`)

```python
MODEL_CASCADE = [
    "groq:openai/gpt-oss-120b",      # strongest — tried first
    "groq:qwen/qwen3.6-27b",         # coding + 262K context
    "groq:llama-3.3-70b-versatile",  # reliable all-rounder
    "groq:qwen/qwen3-32b",           # solid RAG fallback
    "groq:openai/gpt-oss-20b",       # fastest — last resort
]
```

### Memory Config (`src/config.py`)

```python
MEM0_CONFIG = {
    "llm": {
        "provider": "groq",
        "config": {"model": "openai/gpt-oss-20b"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0_research_assistant",
            "embedding_model_dims": 384,
            "path": "./qdrant_store",    # persists to disk across restarts
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
```

---

## Usage

### Natural Language Queries

```
What are the latest breakthroughs in quantum computing?
What does minoxidil do for hair loss and what does the research say?
Explain the difference between RAG and fine-tuning for LLMs
Find me repositories for building agentic AI systems
```

### Slash Commands

| Command | Alias | Description | Tool |
|---|---|---|---|
| `/search <query>` | `/websearch` | Web search only | `web_search` |
| `/papers <topic>` | `/asearch` | arXiv paper search | `arxiv_search` |
| `/paper <id>` | `/arxiv` | Read full arXiv PDF | `fetch_arxiv_paper` |
| `/pubmed <topic>` | `/med` `/medical` | PubMed medical search | `pubmed_search` |
| `/git <query>` | `/github` | GitHub repo search | `github_search` |
| `/yt <query>` | `/youtube` | YouTube video search | `youtube_search` |
| `/sub <video_id>` | `/transcript` | Get video transcript | `youtube_transcript` |

### Tool Toggle Panel

Click the `+` button next to the chat input to enable or disable individual tools per query.

### MCP Server (Standalone)

```bash
python -m src.mcp_server
```

---

## Demo Knowledge Base

### AI & Machine Learning
```
Explain how attention mechanisms work in transformers — find the original paper
What are the key differences between RAG and fine-tuning?
Search for the best open-source LLM agent frameworks on GitHub
```

### Medical & Health Research
```
What does the research say about minoxidil for hair loss?
Find PubMed papers on intermittent fasting and metabolic health
What are the side effects of GLP-1 receptor agonists?
```

### Computer Science
```
What are the latest advances in graph neural networks?
/papers diffusion models image generation
Find tutorials on building RAG systems with LangChain
```

---

## Test Scenarios

**Memory system:**
```bash
python -m tests.test_memory
```
Expected: `SUCCESS: Memory initialized successfully!`

**Module imports:**
```bash
python -m tests.test_imports
```

**End-to-end agent:**
```bash
python -m tests.test_agent
```

### Manual Test Matrix

| Scenario | Input | Expected |
|---|---|---|
| Medical routing | `what does minoxidil do` | Calls `pubmed_search`, not `arxiv_search` |
| CS routing | `explain graph neural networks` | Calls `arxiv_search` + `fetch_arxiv_paper` |
| Slash force tool | `/git langchain agents` | Calls `github_search` directly |
| YouTube cards | `/yt attention is all you need` | Compact thumbnail cards |
| Model cascade | Hit rate limit | Badge in sidebar changes model |
| Memory recall | Topic from a previous session | System prompt includes prior context |
| Tool toggle | Disable arXiv | Agent skips arXiv, uses web only |

---

## Roadmap

| Status | Feature |
|---|---|
| Done | 7-tool ecosystem (web, arXiv, PubMed, YouTube x2, GitHub) |
| Done | 5-model cascade with mid-loop switching |
| Done | Live model indicator (sidebar + per-reply badge) |
| Done | Smart database routing (PubMed vs arXiv) |
| Done | Per-user memory isolation with disk persistence |
| Done | FastMCP server for external integrations |
| Done | Slash command routing with forced tool binding |
| Planned | Semantic Scholar tool for broader academic coverage |
| Planned | PDF upload — research your own documents |
| Planned | Export session as formatted research report |
| Planned | Streaming responses (token-by-token rendering) |
| Planned | Citation graph — visualize paper relationships |
| Planned | Scheduled research digests |

---

## License

This project is provided for educational and personal research use.
