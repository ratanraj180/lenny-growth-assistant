# Lenny Growth Assistant

The Lenny Growth Assistant is a full-stack, RAG-powered chatbot designed to answer growth-related questions strictly based on the transcripts of Lenny's Podcast and Newsletter.

## Features
- **Agentic RAG**: Powered by Anthropic Claude (Cloud) or Ollama (Local) to answer questions based entirely on transcript context.
- **Provider Switching**: Seamlessly switch between Claude and local Llama3 without code changes.
- **Source Grounding**: Every answer cites the exact transcript chunks it used.
- **Ship 30 for 30 Skill**: A dedicated agent skill that writes a 1,250-word essay structured with hooks, headings, and takeaways.
- **Artifact Generation & Viewer**: Safely renders HTML/Markdown artifacts inline within the chat.

## Architecture
- **Frontend**: React + TypeScript + Vite + Tailwind CSS.
- **Backend**: FastAPI (Python 3.11+).
- **Database**: PostgreSQL with `pgvector` for conversational memory and vector similarity search.

## Prerequisites
- Docker (for PostgreSQL)
- Python 3.11+
- Node.js 18+
- Ollama (installed locally)

## Installation & Setup

1. **Clone the repository & data**
   ```bash
   git clone <repo-url>
   cd lenny-growth-assistant
   git clone https://github.com/LennysNewsletter/lennys-newsletterpodcastdata.git data
   ```

2. **Environment Setup (.env)**
   Copy the example and fill in your keys:
   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Start PostgreSQL (pgvector)**
   ```bash
   docker compose up -d
   ```

4. **Pull Local Models (Ollama)**
   ```bash
   ollama pull nomic-embed-text
   ollama pull llama3
   ```

## Running the Backend
1. Activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the ingestion pipeline to load the transcripts into the database:
   ```bash
   cd backend
   export PYTHONPATH="."
   python app/services/ingestion.py
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Running the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies and start Vite:
   ```bash
   npm install
   npm run dev
   ```

## Tests
To run backend tests (mocked DB):
```bash
cd backend
pytest app/tests
```

## Important Decisions
- **Isolation Strategy**: The Artifact Viewer uses a React Markdown renderer or a sandboxed iframe to ensure untrusted AI-generated HTML cannot execute malicious JavaScript in the context of the main app.
- **Local Fallback**: Ollama is supported natively. If `ANTHROPIC_API_KEY` is missing, the system gracefully falls back to local models or throws a readable error if the user insists on a cloud provider.
