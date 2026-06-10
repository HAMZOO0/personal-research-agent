# Personal Research Assistant

An AI-powered research assistant that remembers you across sessions.

Built with **Grok + Mem0 + LangChain + Streamlit**.

## What it does
- Researches any topic using Grok (qwen3-32b)
- Remembers your research interests and past sessions via Mem0
- Builds on previous research so you never repeat context
- Stores only meaningful facts about you, not small talk

## Tech Stack
- [Groq](https://console.groq.com) — LLM inference (qwen3-32b)
- [Mem0](https://mem0.ai) — persistent user memory
- [LangChain](https://langchain.com) — LLM orchestration
- [Streamlit](https://streamlit.io) — frontend UI

#

Personal Research Assistant is an AI-powered app that helps you research any topic deeply and remembers what you've worked on across sessions. Built using Groq (qwen3-32b) for fast LLM inference, Mem0 for persistent user memory, LangChain for orchestration, and Streamlit for the frontend. Unlike normal chatbots that forget everything, this assistant builds on your past research — if you've explored a topic before, it connects new queries to what you already know. It also filters out small talk and only stores meaningful facts about you, keeping memory clean and relevant.