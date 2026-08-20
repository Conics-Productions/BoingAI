from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 3) -> str:
    """Searches DuckDuckGo and returns a formatted text summary of search results."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r['title']}\nSnippet: {r['body']}")
        
        if not results:
            return ""
        
        return "\n\n".join(results)
    except Exception as e:
        print(f"Web search error: {e}")
        return ""