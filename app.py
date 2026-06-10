import streamlit as st
from memory import chat, getAllMemory

st.set_page_config(page_title="Research Assistant", page_icon="🔬", layout="wide")

with st.sidebar:
    USER_ID = st.text_input("Your User ID", value="user_01", placeholder="Enter your user ID...")
# --- Init session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.title("Research Assistant")
    st.caption("Powered by Grok + Mem0 + LangChain")
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

# --- Chat area ---
st.title("Research Assistant")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---
if prompt := st.chat_input("Ask anything to research..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            reply = chat(user_id=USER_ID, user_message=prompt)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})