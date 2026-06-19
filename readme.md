# Personal Research Assistant

An AI-powered research assistant that remembers your past sessions and builds on previous research. Ask questions, get structured answers with citations, and pick up where you left off without repeating context. Now equipped with an autonomous agent loop, web search, and arXiv paper reading tools.

Built with **Groq**, **Mem0**, **LangChain**, **LangGraph**, and **Streamlit**.

![Personal Research Assistant — Main Architecture with Mem0 Memory Layer](public/arct.png)

---

## Architecture

The diagram above shows the full system flow. Below is a simplified interactive view of the agentic workflow:

```mermaid
flowchart TB
    subgraph UI["User Interface"]
        ST[Streamlit Chat UI]
    end

    subgraph Orchestration["Orchestration Layer — LangGraph & LangChain"]
        MR[Memory Retrieval]
        CB[Context Builder]
        AE[ReAct Agent Executor]
        WS[web_search tool]
        FA[fetch_arxiv_paper tool]
    end

    subgraph Memory["Memory Layer — Mem0"]
        MS[memory.search]
        MA[memory.add]
        MG[memory.get_all]
        FE[Fact Extractor]
        FP[Fact Processor]
        EM[Embedder]
        VS[(Qdrant Vector Store)]
    end

    subgraph LLM["LLM Layer — Groq"]
        SP[System Prompt]
        LLM_M[llama-3.3-70b-versatile]
    end

    ST -->|User query| MR
    MR --> MS
    MS --> VS
    VS -->|Relevant memories| CB
    CB -->|Query + memory context| AE
    AE --> SP
    SP --> LLM_M
    AE <-->|Invoke| WS
    AE <-->|Invoke| FA
    LLM_M -->|Structured response| ST
    LLM_M --> MA
    MA --> FE
    FE --> FP
    FP --> EM
    EM --> VS
    ST -->|View memories| MG
    MG --> VS
```

### Request flow

1. User submits a question in the Streamlit UI.
2. LangChain searches Mem0 for relevant past memories for that user.
3. Retrieved memories are injected into the agent's system prompt context.
4. The query, system prompt, and tools are handled by a LangGraph ReAct Agent using `llama-3.3-70b-versatile`.
5. The agent can search the web and fetch full arXiv paper contents to answer the query accurately.
6. The final response is shown to the user, and the conversation is stored in Mem0 for future sessions.

---

## Features

- **Persistent memory** — Mem0 stores meaningful facts from past research per user ID.
- **Context-aware answers** — New questions connect to what you have already explored.
- **Agentic Capabilities** — Uses a LangGraph ReAct agent to autonomously search the web and retrieve research papers.
- **Web Search Tool** — Queries the web using `ddgs` to find the most recent and relevant information.
- **arXiv Paper Fetcher** — Downloads and parses the full text of arXiv papers using `PyMuPDF` if referenced or requested, preventing summarization based on search snippets alone.
- **Structured output** — Responses include sections, source links, and follow-up questions.
- **Memory browser** — View all stored memories from the sidebar.
- **Per-user isolation** — Each user ID has its own memory space.

---

## Tech Stack

| Layer | Technology | Role |
|-------|------------|------|
| Frontend | [Streamlit](https://streamlit.io) | Chat UI and memory viewer |
| Orchestration | [LangChain](https://langchain.com) & [LangGraph](https://langchain-ai.github.io/langgraph/) | Agent assembly, prompt construction, and tool execution |
| LLM | [Groq](https://console.groq.com) — llama-3.3-70b-versatile | Research reasoning and tool-calling agent |
| Web Search | [ddgs](https://pypi.org/project/ddgs/) | Web search tool backend |
| PDF Processing | [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) | Extracting text from downloaded arXiv paper PDFs |
| Memory | [Mem0](https://mem0.ai) | Long-term semantic memory |
| Vector store | Qdrant (in-memory) | Embedding storage and retrieval |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | Text vectorization |

---

## Project Structure

```
Personal research assistant/
├── app.py                  # Streamlit frontend
├── memory.py               # Mem0 + LangChain + LangGraph agent logic
├── test.py                 # Mem0 initialization test script
├── test_agent_arxiv.py     # Test script for testing arXiv paper fetching
├── test_future_imports.py  # Test script for imports verification
├── public/
│   └── arct.png            # Architecture diagram
├── .env                    # API keys (not committed)
└── readme.md
```

---

## Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com)

---

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd "Personal research assistant"
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install streamlit python-dotenv langchain langchain-groq mem0ai qdrant-client sentence-transformers ddgs pymupdf requests langgraph
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Verify Setup and Agents (optional)**

   To verify Mem0 database initialization:
   ```bash
   python test.py
   ```
   You should see `SUCCESS: Memory initialized`.

   To test agent tool execution and arXiv fetching:
   ```bash
   python test_agent_arxiv.py
   ```
   This will run a sample query that forces the agent to fetch and summarize an arXiv paper.

---

## Usage

Start the Streamlit app:

```bash
streamlit run app.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`).

1. Set your **User ID** in the sidebar (default: `user_01`).
2. Type a research question in the chat input.
3. Use **View all memories** to inspect stored facts.
4. Use **Clear chat** to reset the current session UI (memory is preserved).

---

## How Memory Works

When you send a message, Mem0:

1. **Searches** the vector store for memories related to your query.
2. **Injects** relevant facts into the system prompt.
3. **Generates** a response using Groq with that context.
4. **Extracts** new facts from the exchange and stores them for later.

Mem0 uses an in-memory Qdrant instance (`:memory:`), so memories reset when the process stops. For persistent storage across restarts, configure a local or remote Qdrant path in `memory.py`.

---

## Configuration

Key settings in `memory.py`:

| Setting | Value | Description |
|---------|-------|-------------|
| LLM model | `groq:llama-3.3-70b-versatile` | Main agent research & reasoning model |
| Mem0 LLM | `llama-3.3-70b-versatile` | Fact extraction |
| Collection | `mem0_research_assistant` | Qdrant collection name |
| Embedder | `all-MiniLM-L6-v2` | 384-dim embeddings |
| Memory search limit | 5 | Max memories retrieved per query |

---

## License

This project is provided as-is for personal and educational use.
