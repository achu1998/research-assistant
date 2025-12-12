from duckduckgo_search import DDGS
from typing import List, Dict

class SearchTool:
    """Handles internet searches for academic papers and articles."""
    
    def __init__(self):
        self.ddgs = DDGS()

    def search_academic_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Searches for academic context. 
        Note: We append 'arxiv' or 'research paper' to queries to target academic content.
        """
        refined_query = f"{query} research paper arxiv ieee"
        results = []
        
        try:
            # DuckDuckGo Text Search
            search_gen = self.ddgs.text(refined_query, max_results=max_results)
            for r in search_gen:
                results.append({
                    "title": r.get('title'),
                    "href": r.get('href'),
                    "body": r.get('body')
                })
        except Exception as e:
            print(f"Search Error: {e}")
            return []

        return results

    def format_results(self, results: List[Dict]) -> str:
        """Formats search results into a string for the LLM."""
        if not results:
            return "No relevant research papers found."
        
        formatted = "Existing Research Found:\n"
        for i, res in enumerate(results, 1):
            formatted += f"{i}. TITLE: {res['title']}\n   SNIPPET: {res['body']}\n   URL: {res['href']}\n\n"
        return formatted