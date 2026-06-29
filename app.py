import streamlit as st
import json
from src import chat, getAllMemory

st.set_page_config(page_title="Research Assistant", layout="wide")

# Injecting Claude Code-style dark grey theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    .stApp {
        background: #111111;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #161616 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }

    .panel-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #d4d4d4 0%, #a3a3a3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }

    .dashboard-card {
        background: #1a1a1a;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }

    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }

    .dashboard-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }

    .youtube-card:hover {
        border-color: rgba(239, 68, 68, 0.35);
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.1);
    }

    .card-title-link {
        text-decoration: none !important;
        font-weight: 600;
        color: #e5e5e5;
        transition: color 0.2s ease;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.4;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }

    .card-title-link:hover {
        color: #ffffff !important;
    }

    .youtube-card .card-title-link:hover {
        color: #fca5a5 !important;
    }

    .card-badge-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0 0.8rem 0;
        flex-wrap: wrap;
    }

    .badge {
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }

    .badge-stars {
        background-color: rgba(255, 255, 255, 0.06);
        color: #d4d4d4;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .badge-yt {
        background-color: rgba(239, 68, 68, 0.08);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }

    .badge-topic {
        background-color: rgba(255, 255, 255, 0.05);
        color: #a3a3a3;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .card-desc-text {
        font-size: 0.875rem;
        color: #737373;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }

    .action-btn-link {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #d4d4d4;
        text-decoration: none !important;
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 0.3rem 0.65rem;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.04);
    }

    .action-btn-link:hover {
        color: #ffffff !important;
        background-color: #2d2d2d;
        border-color: rgba(255, 255, 255, 0.22);
        transform: translateX(2px);
    }

    .youtube-card .action-btn-link {
        color: #f87171;
        border-color: rgba(239, 68, 68, 0.2);
        background-color: rgba(239, 68, 68, 0.04);
    }

    .youtube-card .action-btn-link:hover {
        color: #ffffff !important;
        background-color: #b91c1c;
        border-color: #b91c1c;
    }

    /* Custom tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #1a1a1a;
        padding: 5px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 7px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #737373;
        background-color: transparent;
        transition: all 0.2s ease;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e5e5e5;
        background-color: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Streamlit container video override */
    .element-container iframe {
        border-radius: 10px !important;
    }

    /* Buttons styling */
    div.stButton > button:first-child {
        background: #242424;
        color: #e5e5e5;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background: #2e2e2e;
        border-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    /* Plus button styling */
    div[data-testid="stPopover"] button {
        background-color: #1e1e1e !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #a3a3a3 !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.35rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        margin-top: 5px !important;
    }
    div[data-testid="stPopover"] button:hover {
        background-color: #2a2a2a !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    USER_ID = st.text_input("Your User ID", value="user_01", placeholder="Enter your user ID...")

# --- Init session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.title("Research Assistant")
    st.caption("Powered by Grok + Mem0 + LangChain + MCP Server")
    st.divider()

    st.subheader("Memory")
    if st.button("View all memories", use_container_width=True):
        memories = getAllMemory(USER_ID)
        items = memories.get("results", []) if isinstance(memories, dict) else memories
        if items:
            for item in items:
                if isinstance(item, dict) and item.get("memory"):
                    st.info(item["memory"])
        else:
            st.caption("No memories yet.")

    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Area (GPT-style Single Column) ---
st.title("Research Assistant")
st.caption("Ask questions, explore papers, search code, and find videos in one unified chat.")

# Message container
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render YouTube results inline for the assistant
        if msg.get("youtube_results"):
            st.markdown('<div class="panel-header" style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">YouTube Insights</div>', unsafe_allow_html=True)
            for yt in msg["youtube_results"]:
                vid = yt.get('video_id', '')
                thumb = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg" if vid else ""
                st.markdown(f"""
                <div class="dashboard-card youtube-card">
                    <a href="{yt.get('url')}" target="_blank">
                        <img src="{thumb}" style="width:100%;border-radius:8px;margin-bottom:0.6rem;" onerror="this.style.display='none'"/>
                    </a>
                    <a href="{yt.get('url')}" target="_blank" class="card-title-link">{yt.get('title', 'Video')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-yt">YouTube</span>
                        <span class="badge badge-topic">ID: {vid}</span>
                    </div>
                    <a href="{yt.get('url')}" target="_blank" class="action-btn-link">Watch on YouTube ➜</a>
                </div>
                """, unsafe_allow_html=True)
                
        # Render GitHub results inline for the assistant
        if msg.get("github_results"):
            st.markdown('<div class="panel-header" style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">GitHub Code Repositories</div>', unsafe_allow_html=True)
            for repo in msg["github_results"]:
                st.markdown(f"""
                <div class="dashboard-card">
                    <a href="{repo.get('url')}" target="_blank" class="card-title-link">Repository: {repo.get('name')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-stars">Stars: {repo.get('stars', 0):,}</span>
                        <span class="badge badge-topic">GitHub Repo</span>
                    </div>
                    <div class="card-desc-text">{repo.get('desc')}</div>
                    <a href="{repo.get('url')}" target="_blank" class="action-btn-link">Explore Code ➜</a>
                </div>
                """, unsafe_allow_html=True)

# --- Tool configurations popover (GPT-style plus button selector) ---
col_pop, col_space = st.columns([1, 10])
with col_pop:
    with st.popover("+", help="Configure active skills"):
        st.markdown("Toggle active skills for this query:")
        tool_options = {
            "Web Search": "web_search",
            "arXiv Paper Search": "arxiv_search",
            "arXiv Paper Reader": "fetch_arxiv_paper",
            "GitHub Repo Search": "github_search",
            "YouTube Video Search": "youtube_search",
        }
        enabled_tools = []
        for label, tool_id in tool_options.items():
            if st.checkbox(label, value=True):
                enabled_tools.append(tool_id)
                # Auto-enable transcript tool when youtube search is active
                if tool_id == "youtube_search":
                    enabled_tools.append("youtube_transcript")
        
        st.divider()
        st.markdown("""
        **Slash Commands:**
        - `/search <query>` — Web Search
        - `/papers <topic>` — arXiv Paper Search
        - `/paper <id>` — Read arXiv Paper by ID
        - `/git <query>` — GitHub Search
        - `/yt <query>` — YouTube Search
        - `/sub <video_id>` — YouTube Transcript
        """)

# --- Chat Input ---
if prompt := st.chat_input("Ask anything or use command (e.g. /yt, /git)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            res = chat(user_id=USER_ID, user_message=prompt, enabled_tools=enabled_tools)
        
        reply = res.get("reply", "No response generated.")
        st.markdown(reply)
        
        yt_data = res.get("youtube_results", [])
        gh_data = res.get("github_results", [])
        
        if yt_data:
            st.markdown('<div class="panel-header" style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">YouTube Insights</div>', unsafe_allow_html=True)
            for yt in yt_data:
                vid = yt.get('video_id', '')
                thumb = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg" if vid else ""
                st.markdown(f"""
                <div class="dashboard-card youtube-card">
                    <a href="{yt.get('url')}" target="_blank">
                        <img src="{thumb}" style="width:100%;border-radius:8px;margin-bottom:0.6rem;" onerror="this.style.display='none'"/>
                    </a>
                    <a href="{yt.get('url')}" target="_blank" class="card-title-link">{yt.get('title', 'Video')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-yt">YouTube</span>
                        <span class="badge badge-topic">ID: {vid}</span>
                    </div>
                    <a href="{yt.get('url')}" target="_blank" class="action-btn-link">Watch on YouTube ➜</a>
                </div>
                """, unsafe_allow_html=True)
                
        if gh_data:
            st.markdown('<div class="panel-header" style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">GitHub Code Repositories</div>', unsafe_allow_html=True)
            for repo in gh_data:
                st.markdown(f"""
                <div class="dashboard-card">
                    <a href="{repo.get('url')}" target="_blank" class="card-title-link">Repository: {repo.get('name')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-stars">Stars: {repo.get('stars', 0):,}</span>
                        <span class="badge badge-topic">GitHub Repo</span>
                    </div>
                    <div class="card-desc-text">{repo.get('desc')}</div>
                    <a href="{repo.get('url')}" target="_blank" class="action-btn-link">Explore Code ➜</a>
                </div>
                """, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "youtube_results": yt_data,
        "github_results": gh_data
    })
    st.rerun()