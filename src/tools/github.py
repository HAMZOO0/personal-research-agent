import json
import requests

def github_search_tool(query: str) -> str:
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
