import io
import re
import xml.etree.ElementTree as ET
import requests
import fitz  # PyMuPDF


def arxiv_search_tool(query: str, max_results: int = 5) -> str:
    """Search arXiv for papers matching a topic and return IDs, titles, authors, and abstracts."""
    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        r = requests.get(
            "https://export.arxiv.org/api/query",
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        r.raise_for_status()

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(r.text)
        entries = root.findall("atom:entry", ns)

        if not entries:
            return f"No arXiv papers found for query: {query}"

        results = []
        for entry in entries:
            raw_id = entry.find("atom:id", ns).text.strip()
            arxiv_id = raw_id.split("/abs/")[-1].replace("v1", "").replace("v2", "").strip("/")
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            abstract = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            published = entry.find("atom:published", ns).text[:10]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
            author_str = ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else "")

            results.append(
                f"ID: {arxiv_id}\n"
                f"Title: {title}\n"
                f"Authors: {author_str}\n"
                f"Published: {published}\n"
                f"Abstract: {abstract[:500]}{'...' if len(abstract) > 500 else ''}\n"
                f"URL: https://arxiv.org/abs/{arxiv_id}\n"
                f"PDF: https://arxiv.org/pdf/{arxiv_id}"
            )

        return "\n\n" + ("-" * 60 + "\n\n").join(results)

    except Exception as e:
        return f"Error searching arXiv: {str(e)}"


def fetch_arxiv_paper_tool(arxiv_id_or_url: str) -> str:
    """Download and extract the text content of an arXiv research paper.
    
    This tool is useful when you have an arXiv ID (like '2310.01526') or an arXiv URL (like 'https://arxiv.org/abs/2310.01526')
    and want to read the paper's contents, abstract, introduction, or main findings.
    """
    print("\n\n\n\n\narxiv_id_or_url:: ", arxiv_id_or_url)
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
