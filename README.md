# SourceLens AI

SourceLens AI is a placement-focused multi-agent research assistant. Phase 1 implements a clean local-first research workflow using Streamlit, LangGraph, free public search APIs, and Ollama.

## Phase 1 Scope

Implemented workflow:

```text
User Query
-> Planner Agent
-> Search Agent
-> Summarization Agent
-> Markdown Report
```

Phase 1 intentionally does not include verification, RAG, document uploads, ChromaDB, SQLite persistence, Docker, PDF export, Gemini, or research history.

## Features

- Streamlit user interface
- LangGraph workflow orchestration
- Planner agent that creates subquestions and search queries
- Free search agent using Wikipedia MediaWiki API and OpenAlex
- Ollama local-first summarization agent
- Fallback summarization when Ollama is unavailable
- Markdown report generation
- Basic tests for configuration, reports, and workflow structure

## Requirements

- Python 3.10+
- Ollama installed locally for LLM summaries
- A local Ollama model, for example:

```powershell
ollama pull llama3.1
```

The application still produces a basic extractive report if Ollama is unavailable.

SourceLens AI uses Ollama's local chat API:

```text
GET  /api/tags
POST /api/chat
```

If `SOURCELENS_OLLAMA_MODEL` is set to `llama3.1` and your installed model is
`llama3.1:latest`, the app will automatically use the installed tag.

## Search Reliability Note

Phase 1 avoids scraping DuckDuckGo's HTML search pages because those endpoints can return `202 RateLimit` responses during local development. The Search Agent uses the official Wikipedia MediaWiki API with a compliant user agent, plus OpenAlex for lightweight academic sources.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

If your system uses the Python launcher:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Configuration

Environment variables are optional. Defaults are defined in `app/core/config.py`.

```text
SOURCELENS_APP_NAME=SourceLens AI
SOURCELENS_LOG_LEVEL=INFO
SOURCELENS_OLLAMA_BASE_URL=http://localhost:11434
SOURCELENS_OLLAMA_MODEL=llama3.1
SOURCELENS_OLLAMA_TIMEOUT_SECONDS=60
SOURCELENS_SEARCH_MAX_RESULTS=5
SOURCELENS_SEARCH_TIMEOUT_SECONDS=20
SOURCELENS_SEARCH_USER_AGENT=SourceLensAI/1.0 (local placement project; contact: sourcelens-local@example.com)
SOURCELENS_REPORT_OUTPUT_DIR=data/reports
```

## Run

```powershell
streamlit run app/main.py
```

Then open the URL Streamlit prints, usually `http://localhost:8501`.

## Project Structure

```text
app/
  agents/
  core/
  graph/
  providers/
  reports/
  services/
  ui/
  utils/
tests/
```

## Future Phases

The current code is intentionally modular so later phases can add:

- Verification Agent
- ChromaDB and RAG
- PDF/DOCX/TXT ingestion
- SQLite research history
- PDF report export
- Gemini optional provider
- Docker support

These additions can be introduced as new providers, services, and LangGraph nodes without rewriting the Phase 1 UI or core workflow.
