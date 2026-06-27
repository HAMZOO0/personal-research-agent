import streamlit as st
import json
from src import chat, getAllMemory

st.set_page_config(page_title="Research Assistant", layout="wide")

# Injecting premium custom CSS styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 10% 20%, #080711 0%, #0f1026 90%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(8, 7, 17, 0.85) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
    }
    
    .panel-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        text-shadow: 0 0 40px rgba(129, 140, 248, 0.15);
    }
    
    .dashboard-card {
        background: linear-gradient(145deg, rgba(25, 28, 50, 0.65) 0%, rgba(15, 17, 32, 0.75) 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
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
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
    }
    
    .dashboard-card:hover {
        transform: translateY(-3px);
        border-color: rgba(129, 140, 248, 0.35);
        box-shadow: 0 15px 35px -5px rgba(129, 140, 248, 0.2), 0 0 15px 0 rgba(129, 140, 248, 0.05);
    }
    
    .youtube-card:hover {
        border-color: rgba(239, 68, 68, 0.4);
        box-shadow: 0 15px 35px -5px rgba(239, 68, 68, 0.2), 0 0 15px 0 rgba(239, 68, 68, 0.05);
    }
    
    .card-title-link {
        text-decoration: none !important;
        font-weight: 600;
        color: #f8fafc;
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
        color: #818cf8 !important;
    }
    
    .youtube-card .card-title-link:hover {
        color: #f87171 !important;
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
        background-color: rgba(234, 179, 8, 0.1);
        color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.2);
    }
    
    .badge-yt {
        background-color: rgba(239, 68, 68, 0.1);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    .badge-topic {
        background-color: rgba(129, 140, 248, 0.1);
        color: #93c5fd;
        border: 1px solid rgba(129, 140, 248, 0.2);
    }
    
    .card-desc-text {
        font-size: 0.875rem;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }
    
    .action-btn-link {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #818cf8;
        text-decoration: none !important;
        transition: all 0.2s ease;
        border: 1px solid rgba(129, 140, 248, 0.25);
        padding: 0.3rem 0.65rem;
        border-radius: 8px;
        background-color: rgba(129, 140, 248, 0.05);
    }
    
    .action-btn-link:hover {
        color: #ffffff !important;
        background-color: #4f46e5;
        border-color: #4f46e5;
        transform: translateX(3px);
    }
    
    .youtube-card .action-btn-link {
        color: #f87171;
        border-color: rgba(239, 68, 68, 0.25);
        background-color: rgba(239, 68, 68, 0.05);
    }
    
    .youtube-card .action-btn-link:hover {
        color: #ffffff !important;
        background-color: #dc2626;
        border-color: #dc2626;
    }
    
    /* Custom tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #94a3b8;
        background-color: transparent;
        transition: all 0.2s ease;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(129, 140, 248, 0.15) !important;
        color: #ffffff !important;
        border: 1px solid rgba(129, 140, 248, 0.25) !important;
    }
    
    /* Streamlit container video override */
    .element-container iframe {
        border-radius: 12px !important;
    }

    /* Buttons styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        transform: translateY(-1px);
    }
    
    /* Plus button styling */
    div[data-testid="stPopover"] button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #94a3b8 !important;
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
        background-color: rgba(129, 140, 248, 0.15) !important;
        border-color: rgba(129, 140, 248, 0.3) !important;
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
                st.markdown(f"""
                <div class="dashboard-card youtube-card">
                    <a href="{yt.get('url')}" target="_blank" class="card-title-link">Video: {yt.get('title', 'Video')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-yt">YouTube</span>
                        <span class="badge badge-topic">ID: {yt.get('video_id')}</span>
                    </div>
                    <a href="{yt.get('url')}" target="_blank" class="action-btn-link">View Video ➜</a>
                </div>
                """, unsafe_allow_html=True)
                st.video(yt.get('url'))
                
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
            "GitHub Repo Search": "github_search",
            "YouTube Video Search": "youtube_search",
            "arXiv Paper Fetcher": "fetch_arxiv_paper"
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
        **Keyboard Commands:**
        - `/search <query>` - Web Search
        - `/git <query>` - GitHub Search
        - `/yt <query>` - YouTube Search
        - `/paper <id>` - arXiv Paper
        - `/sub <video_id>` - YouTube Transcript
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
                st.markdown(f"""
                <div class="dashboard-card youtube-card">
                    <a href="{yt.get('url')}" target="_blank" class="card-title-link">Video: {yt.get('title', 'Video')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-yt">YouTube</span>
                        <span class="badge badge-topic">ID: {yt.get('video_id')}</span>
                    </div>
                    <a href="{yt.get('url')}" target="_blank" class="action-btn-link">View Video ➜</a>
                </div>
                """, unsafe_allow_html=True)
                st.video(yt.get('url'))
                
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