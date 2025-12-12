import httpx
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

class LLMClient:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.timeout = 1200.0 # 5 minutes per thought

    def generate(self, prompt: str, system_prompt: str, json_mode: bool = False) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "temperature": 0.2, # Low temp for precision
        }
        
        if json_mode:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            raise Exception(f"LLM Error: {str(e)}")

    def extract_search_queries(self, idea_text: str) -> dict:
        """Generates targeted search queries based on the idea."""
        system = "You are a Senior Research Librarian. Generate 3 specific academic search queries to find existing literature that matches the user's research idea."
        prompt = f"""Research Idea: {idea_text}
        
        Return JSON format: {{ "queries": ["query1", "query2", "query3"] }}"""
        
        response = self.generate(prompt, system, json_mode=True)
        return json.loads(response)

    def evaluate_novelty(self, current_idea: str, search_results: str) -> dict:
        """
        CRITICAL STEP: Determines if the idea exists and pivots if necessary.
        """
        system = """You are a rigorous Ph.D. Advisor. 
        Your goal is to determine if a research idea is NOVEL based on search results.
        
        1. Compare the Current Idea against the Search Results.
        2. If the idea is already solved or heavily researched in the results, it is NOT NOVEL.
        3. If it is NOT NOVEL, you must propose a 'Refined Idea' that pivots, adds a constraint, or changes the methodology to make it unique.
        4. If it IS NOVEL, the Refined Idea should be the same as the Current Idea.
        
        Return JSON."""
        
        prompt = f"""
        CURRENT IDEA: 
        {current_idea}

        SEARCH RESULTS OF EXISTING WORK:
        {search_results}

        Task:
        1. specific_collision: Cite the specific paper from results that conflicts (if any).
        2. is_novel: Boolean (true/false).
        3. reasoning: Why is it novel or not?
        4. refined_idea_text: The new version of the idea (or the same if novel).

        Output JSON format:
        {{
            "specific_collision": "Title of conflicting paper or None",
            "is_novel": boolean,
            "reasoning": "string",
            "refined_idea_text": "string"
        }}
        """
        response = self.generate(prompt, system, json_mode=True)
        return json.loads(response)

    def write_proposal(self, final_idea: str) -> str:
        """Writes the final research proposal."""
        system = "You are a Grant Writer. Write a precise, formal research abstract and methodology for this novel idea."
        prompt = f"Idea: {final_idea}\n\nWrite a markdown formatted Research Proposal including Title, Abstract, Methodology, and Expected Contribution."
        return self.generate(prompt, system, json_mode=False)