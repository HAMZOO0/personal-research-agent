from ddgs import DDGS

def web_search_tool(query: str) -> str:
    """Search the web for the latest information on a topic."""
    try:
        print("\n\n\n\n\nquery:: ", query)
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))
        
        output = []
        for i, r in enumerate(results, 1):
            output.append(
                f"[{i}] {r['title']}\n"
                f"    Source URL: {r['href']}\n"
                f"    Summary: {r['body']}\n"
            )
        return "\n" + ("-" * 60 + "\n").join(output)
    except Exception as e:
        return f"Error performing web search: {str(e)}"
