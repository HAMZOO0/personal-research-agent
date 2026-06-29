import os
from mcp.server.fastmcp import FastMCP
from src.tools.search import web_search_tool
from src.tools.arxiv import arxiv_search_tool, fetch_arxiv_paper_tool
from src.tools.youtube import youtube_search_tool, youtube_transcript_tool
from src.tools.github import github_search_tool

mcp = FastMCP("ResearchAssistantTools")

@mcp.tool(name="web_search")
def web_search(query: str) -> str:
    """Search the web for the latest information on a topic."""
    return web_search_tool(query)

@mcp.tool(name="arxiv_search")
def arxiv_search(query: str) -> str:
    """Search arXiv for research papers on a topic.
    Returns paper IDs, titles, authors, publication dates, abstracts, and URLs.
    """
    return arxiv_search_tool(query)

@mcp.tool(name="fetch_arxiv_paper")
def fetch_arxiv_paper(arxiv_id_or_url: str) -> str:
    """Download and extract the text content of an arXiv research paper.
    
    This tool is useful when you have an arXiv ID (like '2310.01526') or an arXiv URL (like 'https://arxiv.org/abs/2310.01526')
    and want to read the paper's contents, abstract, introduction, or main findings.
    """
    return fetch_arxiv_paper_tool(arxiv_id_or_url)

@mcp.tool(name="youtube_search")
def youtube_search(query: str) -> str:
    """Search YouTube for videos related to a topic.
    Returns a JSON string listing video titles, URLs, and video IDs.
    """
    return youtube_search_tool(query)

@mcp.tool(name="youtube_transcript")
def youtube_transcript(video_id: str) -> str:
    """Fetch the transcript of a YouTube video by its video ID or URL.
    Returns the joined text of the transcript.
    """
    return youtube_transcript_tool(video_id)

@mcp.tool(name="github_search")
def github_search(query: str) -> str:
    """Search GitHub for repositories matching a query.
    Returns a JSON string of repositories with their name, stars, URL, and description.
    """
    return github_search_tool(query)

if __name__ == "__main__":
    mcp.run()
