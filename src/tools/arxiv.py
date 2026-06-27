import io
import re
import requests
import fitz  # PyMuPDF

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
