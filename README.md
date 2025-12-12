# NoveltyAI – Recursive Research Assistant

NoveltyAI is a Streamlit-based AI assistant that helps researchers iteratively refine an initial research idea into a more novel, publication-ready proposal.It generates targeted academic search queries, scans web literature, and repeatedly adjusts the idea until a sufficiently novel angle is found or a configurable loop limit is reached.

---

## Features

- **Recursive novelty loop**  
  Evaluates whether a research idea is already covered in existing literature and refines it when conflicts are detected, up to `MAX_REFINEMENT_LOOPS` iterations.

- **Academic web search**  
  Uses DuckDuckGo via `DDGS` and augments queries with academic keywords (e.g., “research paper”, “arxiv”, “ieee”) to bias results toward scholarly content.

- **LLM-powered reasoning and proposal writing**  
  - Generates focused search queries from your idea.  
  - Assesses novelty and produces refined ideas if needed.  
  - Writes a final Markdown research proposal with Title, Abstract, Methodology, and Expected Contribution.

- **Streamlit dashboard UI**  
  - Input via free-text or uploaded PDF concept paper.  
  - Live progress using `st.status` messages.  
  - Visual history of refinement cycles, including conflicts and reasoning.

- **Configurable behaviour**  
  Environment-based control of LLM provider, model, loop limits, search result count, and similarity threshold.

---

## Project Structure

├── streamlit_app.py # Streamlit UI and app entrypoint
├── research_agent.py # Orchestrates the iterative research loop
├── llm_client.py # LLM HTTP client and prompt wrappers
├── search_tool.py # DuckDuckGo-based academic search helper
├── document_processor.py # PDF-to-text extraction for uploaded concept papers
├── config.py # Environment-driven configuration
└── requirements.txt # Python dependencies

---

## Installation

### 1. Clone the repository

git clone <your-repo-url>.git
cd <your-repo-folder>


### 2. Create and activate a virtual environment (recommended)

python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate


### 3. Install dependencies

pip install -r requirements.txt


This installs Streamlit, `httpx`, `duckduckgo-search`, `python-dotenv`, and other required libraries listed in `requirements.txt`.

---

## Configuration

Configuration values are loaded from environment variables via `python-dotenv` in `config.py`. Create a `.env` file in the project root with entries like:

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
MAX_REFINEMENT_LOOPS=5
SEARCH_RESULTS_PER_ITERATION=5
SIMILARITY_THRESHOLD=0.85


Key options:

- `LLM_PROVIDER` – Name of the LLM backend (currently structured around Ollama but extendable).
- `OLLAMA_BASE_URL` – Base URL for the Ollama server (e.g., `http://localhost:11434`). 
- `OLLAMA_MODEL` – Model identifier (e.g., a Llama 3 or Qwen reasoning model).
- `MAX_REFINEMENT_LOOPS` – Maximum refinement iterations to avoid infinite loops.
- `SEARCH_RESULTS_PER_ITERATION` – Maximum number of web results per query.
- `SIMILARITY_THRESHOLD` – Conceptual control for how strict novelty determination should be.

Ensure an Ollama server is running and accessible at `OLLAMA_BASE_URL` before starting the app.

---

## Running the App

From the project root, run:

streamlit run streamlit_app.py


Streamlit will print a local URL (typically `http://localhost:8501`) that you can open in your browser to access the UI.

---

## Usage

### 1. Provide your research idea

In the sidebar:

- Choose **Input Method**:
  - **Text Box** – Type or paste your research idea or hypothesis into the textarea.  
  - **Upload PDF** – Upload a concept paper in PDF format; the `DocumentProcessor` extracts its text and confirms successful loading.

### 2. Start the research loop

Click **“Start Research Loop”**. The button is only enabled when valid text input is available. A `st.status` container appears and shows:

- Initialization message (“Initializing Research Agent…”).  
- Per-iteration updates such as “Iteration N – Analyzing novelty…” and messages when conflicts are discovered or when a novel idea is found.

### 3. Review results

After the loop completes:

- If a **novel idea** is found within the loop limit:
  - A **“Final Novel Research Proposal”** section displays the generated Markdown proposal.  
  - A balloon animation is triggered as visual feedback.

- If **no purely novel idea** is identified:
  - A warning explains that no fully novel angle was found within the maximum loop limit.  
  - The best refined idea is shown as the “Best Attempt”.

Open **“See Refinement History”** to inspect each iteration, including:

- Iteration number.  
- Whether it was marked **NOVEL** or **Conflict found**.  
- The `specific_collision` description, if any.  
- LLM reasoning summarizing why the idea was considered novel or not.

---

## How It Works (Under the Hood)

### LLMClient (`llm_client.py`)

`LLMClient` wraps an HTTP LLM endpoint (Ollama-style) and centralizes all prompts.

- `generate(prompt, system_prompt, json_mode=False)`  
  Sends `model`, `prompt`, `system`, `temperature`, and optional JSON formatting instructions to `/api/generate`, with a generous timeout for deep reasoning.

- `extract_search_queries(idea_text)`  
  Asks the LLM (acting as a “Senior Research Librarian”) to produce three focused academic search queries and returns them as a JSON object.

- `evaluate_novelty(current_idea, search_results)`  
  Frames the LLM as a rigorous PhD advisor, comparing the current idea to the provided search context and returning JSON with `is_novel`, `specific_collision`, `reasoning`, and `refined_idea_text`.

- `write_proposal(final_idea)`  
  Prompts the LLM as a grant writer to output a Markdown research proposal with the required sections.

### SearchTool (`search_tool.py`)

`SearchTool` handles academic-style web search using DuckDuckGo.

- `search_academic_papers(query, max_results=5)`  
  Appends “research paper arxiv ieee” to the query, calls `DDGS.text`, and collects `title`, `href`, and `body` for each result.

- `format_results(results)`  
  Formats results into a numbered, human-readable block labeled “Existing Research Found” to feed into the LLM’s novelty check.

### ResearchAgent (`research_agent.py`)

`ResearchAgent` is the core orchestration layer.

- Holds instances of `LLMClient` and `SearchTool`.  
- Tracks a `logs` list for debugging or inspection.

`run_research_loop(initial_idea, progress_callback=None)` performs:

1. Initialize `current_idea` and iteration counter; reset `is_novel` and `history`.
2. For each iteration while `iteration < MAX_REFINEMENT_LOOPS` and not `is_novel`:
   - Optionally call the `progress_callback` with a status message (used by Streamlit).  
   - Use `LLMClient.extract_search_queries` to get three queries.  
   - For each query, call `SearchTool.search_academic_papers` and aggregate all results.  
   - Format the combined results with `SearchTool.format_results`.  
   - Call `LLMClient.evaluate_novelty` with the current idea and formatted search context.  
   - Append iteration data (idea, novelty flag, collision, reasoning) to `history`.  
   - If not novel, update `current_idea` to `refined_idea_text`, log a refinement message, and continue.  
   - If novel, log success and exit the loop.

3. If `is_novel` at the end, call `write_proposal` and return a success payload containing the final proposal, refined idea, and history; otherwise return a failure payload with the best refined idea and full history.

### Streamlit UI (`streamlit_app.py`)

The Streamlit app ties everything together.

- Configures page title, icon, and a wide layout, and injects some CSS to style the status boxes.
- Renders the sidebar controls for input method and content, plus the “Start Research Loop” button. 
- Uses a `st.status` context manager to show dynamic progress messages and final completion status, then displays either the final proposal or the best attempt along with the refinement history.