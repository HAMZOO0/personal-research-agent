# Personal Research Assistant (Modular Agent Framework)

An AI-powered research assistant that remembers your past sessions and builds on previous research. Ask questions, get structured answers with citations, and pick up where you left off without repeating context. Now equipped with an autonomous agent loop, web search, and arXiv paper reading tools.

Built with **Groq**, **Mem0**, **LangChain**, **LangGraph**, **FastMCP**, and **Streamlit**.

![Personal Research Assistant — Main Architecture with Mem0 Memory Layer](public/arct.png)

---

## Architecture & System Design

Below is the updated system design showing the modular separation of concerns. The main application launches a Streamlit dashboard, which imports the orchestrating assistant module (`src`). The orchestrator interacts with the Mem0 long-term memory layer and coordinates the LangGraph ReAct agent loop, which dynamically spawns and communicates with the `FastMCP` tools server over standard I/O channels.

```mermaid
flowchart TB
    subgraph UI ["User Interface (Streamlit)"]
        app["app.py (Streamlit Dashboard)"]
    end

    subgraph Core ["Modular Codebase (src package)"]
        init["src/__init__.py (Interface)"]
        config["src/config.py (Config & Prompts)"]
        agent["src/agent.py (Agent Executor & Orchestrator)"]
        memory["src/memory.py (Mem0 Memory Wrapper)"]
        mcp_server["src/mcp_server.py (FastMCP Server)"]
    end

    subgraph Tools ["Custom Tools Module (src/tools)"]
        search["tools/search.py (DuckDuckGo Web Search)"]
        arxiv["tools/arxiv.py (arXiv PDF Parser)"]
        youtube["tools/youtube.py (YT Search & Transcripts)"]
        github["tools/github.py (GitHub Repo Search)"]
    end

    subgraph External ["External Services & Models"]
        Groq["Groq (llama-3.3-70b-versatile)"]
        Qdrant["Qdrant Vector Database (:memory:)"]
        ExternalAPIs["External APIs (Arxiv, YouTube, GitHub)"]
    end

    %% UI to Core Interactions
    app -->|Import & Call chat() / getAllMemory()| init
    init --> agent
    init --> memory

    %% Core Package Relationships
    agent -->|Retrieve Relevant Context| memory
    agent -->|Load Configuration| config
    memory -->|Load Vector Config| config
    
    %% Agent to MCP Tool Execution Flow
    agent -->|Execute Subprocess: python -m src.mcp_server| mcp_server
    mcp_server -->|Routes Tool Requests| search
    mcp_server -->|Routes Tool Requests| arxiv
    mcp_server -->|Routes Tool Requests| youtube
    mcp_server -->|Routes Tool Requests| github

    %% Core to External/Service interactions
    agent -->|Chat Completion & Tool Calling| Groq
    memory -->|Store/Retrieve Facts| Qdrant
    search -->|Scraping / DDGS| ExternalAPIs
    arxiv -->|Fetch PDF| ExternalAPIs
    youtube -->|Scrap Transcripts| ExternalAPIs
    github -->|Fetch Repo Data| ExternalAPIs
```

### Request Flow
1. **User Query:** The user enters a prompt in the Streamlit UI (`app.py`).
2. **Context Retrieval:** The orchestrator retrieves semantic memory facts for the user ID using `src.memory.get_memories`.
3. **Prompt Customization:** Memory context is formatted and injected into `SYSTEM_PROMPT_TEMPLATE` from `src.config`.
4. **Agent Invocation:** A LangGraph ReAct agent is initialized in `src.agent.chat`.
5. **Tool Loading & MCP Resolution:** The agent connects to `src.mcp_server` as an external MCP server, loading tools (`web_search`, `fetch_arxiv_paper`, `youtube_search`, `youtube_transcript`, `github_search`).
6. **Execution Loop:** The LLM reasoning determines if a tool needs to be executed:
   - Tool calls are sent to `mcp_server`, which delegates to the respective submodule in `src/tools/`.
   - Results are fed back to the LLM.
7. **Fact Summarization:** The final reply is rendered on Streamlit, and new facts are asynchronously extracted and saved into the vector store by Mem0 via `src.memory.add_memory`.

---

## Directory Structure

The project has been refactored into a proper modular Python structure, clean of root file pollution, and organized as follows:

```
Personal research assistant/
├── app.py                      # Main Streamlit dashboard (Entrypoint)
├── requirements.txt            # System dependencies
├── .env                        # Local secret configurations (Ignored)
├── .gitignore                  # Git ignore files
├── readme.md                   # System design and developer documentation
├── public/                     # Images and structural diagrams
│   └── arct.png                # Structural workflow diagram
├── src/                        # Core application module
│   ├── __init__.py             # Main module entry point (exposes chat, getAllMemory)
│   ├── config.py               # Memory parameters, LLM options, prompts
│   ├── agent.py                # Agent instantiation, chat logic, tool integration
│   ├── memory.py               # Mem0 memory lifecycle management
│   ├── mcp_server.py           # FastMCP server wrapping agent tools
│   └── tools/                  # Subpackage containing modular tool implementations
│       ├── __init__.py         # Exposes all tool functions
│       ├── arxiv.py            # arXiv fetching and parsing logic
│       ├── github.py           # GitHub repository search logic
│       ├── search.py           # DuckDuckGo search logic
│       └── youtube.py          # YouTube video search and transcripts fetching
└── tests/                      # Unified testing package
    ├── __init__.py             # Test package initialization
    ├── test_agent.py           # Validates agent tool-calling logic using sample query
    ├── test_imports.py         # Verifies compatibility and library imports
    └── test_memory.py          # Tests Mem0 initialization and embedding extraction
```

---

## Features

- **Modular Refactoring** — Clear package organization under `src/` keeping the root neat.
- **MCP Tool Execution** — Custom tools are run through a standardized `FastMCP` architecture.
- **Persistent Semantic Memory** — Mem0 remembers facts, constraints, and research steps per User ID.
- **Isolated Per-User Profiles** — Stored data is partitioned by User ID for multi-tenant isolation.
- **YouTube Insights** — Integrates YouTube search results and video transcript analysis tool.
- **GitHub Repository Analytics** — Searches codebases, repositories, and stars.
- **arXiv PDF Reader** — Fetches full PDF content to extract exact details rather than relying on brief search descriptions.

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Personal research assistant"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## Verification & Testing

Verify that the system compiles and works correctly by running the tests module:

- **Verify Memory System Initialization:**
  ```bash
  python -m tests.test_memory
  ```
  Expected output: `SUCCESS: Memory initialized successfully!`

- **Verify Module Imports:**
  ```bash
  python -m tests.test_imports
  ```
  Expected output: Success notifications for LangChain and LangGraph imports.

- **Verify Agent Tool-Calling and arXiv Parsing:**
  ```bash
  python -m tests.test_agent
  ```
  Expected output: The agent will download, read, and summarize the arXiv paper details successfully.

---

## Running the Application

Launch the Streamlit client server:

```bash
streamlit run app.py
```

Open the local URL (typically `http://localhost:8501`) in your browser to interact with the assistant.

---

## License
This project is provided as-is for educational and personal research use.
