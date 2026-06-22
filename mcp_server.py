import os
import io
import re
import urllib.parse
import json
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from ddgs import DDGS
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

# Create FastMCP server
mcp = FastMCP("ResearchAssistantTools")

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for the latest information on a topic."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=2))
        
        output = []
        for r in results:
            output.append(
                f"Title: {r['title']}\nURL: {r['href']}\nDescription:\n{r['body']}\n"
            )
        return "\n" + ("-" * 50 + "\n").join(output)
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@mcp.tool()
def fetch_arxiv_paper(arxiv_id_or_url: str) -> str:
    """Download and extract the text content of an arXiv research paper.
    
    This tool is useful when you have an arXiv ID (like '2310.01526') or an arXiv URL (like 'https://arxiv.org/abs/2310.01526')
    and want to read the paper's contents, abstract, introduction, or main findings.
    """
    try:
        # Extract the arXiv ID from URL or input
        input_str = arxiv_id_or_url.strip()
        match = re.search(r"arxiv\.org/(?:abs|pdf)/([a-zA-Z0-9./\-]+)", input_str, re.IGNORECASE)
        if match:
            arxiv_id = match.group(1)
            if arxiv_id.endswith(".pdf"):
                arxiv_id = arxiv_id[:-4]
        else:
            arxiv_id = input_str

        url = f"https://arxiv.org/pdf/{arxiv_id}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        response.raise_for_status()
        
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
        
        text = ""
        for page in doc:
            text += page.get_text()
        
        if not text.strip():
            return f"Error: No text could be extracted from the arXiv paper with ID {arxiv_id}."
            
        # Truncate to a reasonable limit to avoid context window overflow
        max_chars = 12000
        if len(text) > max_chars:
            truncated_text = text[:max_chars]
            return (
                f"--- arXiv Paper ID: {arxiv_id} (Truncated to first {max_chars} characters) ---\n\n"
                f"{truncated_text}\n\n"
                f"--- [End of Truncated Content - Total Paper Length: {len(text)} characters] ---"
            )
            
        return f"--- arXiv Paper ID: {arxiv_id} ---\n\n{text}"
        
    except Exception as e:
        return f"Error downloading or parsing the arXiv paper: {str(e)}"

@mcp.tool()
def youtube_search(query: str) -> str:
    """Search YouTube for videos related to a topic.
    Returns a JSON string listing video titles, URLs, and video IDs.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        results = []
        matches = re.finditer(r'"videoRenderer":\{"videoId":"(?P<id>[^"]{11})".*?"title":\{"runs":\[\{"text":"(?P<title>[^"]+)"\}\]', r.text)
        seen = set()
        for m in matches:
            vid = m.group("id")
            if vid not in seen:
                seen.add(vid)
                title = m.group("title").encode().decode('unicode-escape', errors='ignore')
                results.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "video_id": vid
                })
                if len(results) >= 5:
                    break
        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": f"Error searching YouTube: {str(e)}"}])

@mcp.tool()
def youtube_transcript(video_id: str) -> str:
    """Fetch the transcript of a YouTube video by its video ID or URL.
    Returns the joined text of the transcript.
    """
    try:
        # Extract video ID if a full URL was passed
        video_id = video_id.strip()
        match = re.search(r'(?:v=|\/embed\/|\/1\/|\/v\/|https:\/\/youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})', video_id)
        if match:
            video_id = match.group(1)
            
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        text = " ".join([t.text for t in transcript])
        return text
    except Exception as e:
        return f"Error fetching YouTube transcript: {str(e)}"

@mcp.tool()
def github_search(query: str) -> str:
    """Search GitHub for repositories matching a query.
    Returns a JSON string of repositories with their name, stars, URL, and description.
    """
    try:
        url = "https://api.github.com/search/repositories"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        results = []
        for repo in data.get("items", []):
            results.append({
                "name": repo["full_name"],
                "stars": repo["stargazers_count"],
                "url": repo["html_url"],
                "desc": repo["description"] or "No description"
            })
        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": f"Error searching GitHub: {str(e)}"}])

if __name__ == "__main__":
    mcp.run()
