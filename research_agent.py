from llm_client import LLMClient
from search_tool import SearchTool
from config import MAX_REFINEMENT_LOOPS
import time

class ResearchAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.search = SearchTool()
        self.logs = []

    def log(self, message: str):
        self.logs.append(message)

    def run_research_loop(self, initial_idea: str, progress_callback=None):
        current_idea = initial_idea
        iteration = 0
        is_novel = False
        
        history = []

        while iteration < MAX_REFINEMENT_LOOPS and not is_novel:
            iteration += 1
            if progress_callback:
                progress_callback(f"Iteration {iteration}: Analyzing novelty...")

            # 1. Generate Search Queries
            queries_data = self.llm.extract_search_queries(current_idea)
            queries = queries_data.get('queries', [])
            self.log(f"Cycle {iteration} Queries: {queries}")

            # 2. Perform Search
            all_results = []
            for q in queries:
                res = self.search.search_academic_papers(q, max_results=3)
                all_results.extend(res)
            
            search_context = self.search.format_results(all_results)

            # 3. Evaluate Novelty & Refine
            evaluation = self.llm.evaluate_novelty(current_idea, search_context)
            
            is_novel = evaluation['is_novel']
            reasoning = evaluation['reasoning']
            collision = evaluation['specific_collision']
            
            history.append({
                "iteration": iteration,
                "idea_state": current_idea,
                "novelty_check": is_novel,
                "collision": collision,
                "reasoning": reasoning
            })

            if not is_novel:
                if progress_callback:
                    progress_callback(f"Cycle {iteration}: Idea exists ({collision}). Refining...")
                current_idea = evaluation['refined_idea_text']
            else:
                if progress_callback:
                    progress_callback(f"Cycle {iteration}: NOVEL IDEA FOUND!")

        # Final Step: Generate Proposal
        final_proposal = self.llm.write_proposal(current_idea)
        
        return {
            "success": is_novel,
            "final_proposal": final_proposal,
            "refined_idea": current_idea,
            "history": history
        }