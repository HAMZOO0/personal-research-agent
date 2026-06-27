from ddgs import DDGS

def web_search_tool(query: str) -> str:
    """Search the web for the latest information on a topic."""
    try:
        print("\n\n\n\n\nquery:: ", query)
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
