# System Architecture

## Component Boundaries
1. **Frontend (React/Vite)**: Handles presentation, session management state, and secure artifact rendering.
2. **Backend (FastAPI)**: Routes requests, manages DB transactions, orchestrates the Agent, and handles RAG retrieval.
3. **Database (PostgreSQL + pgvector)**: Centralized store for relational data (sessions, messages) and vector data (transcript embeddings).
4. **LLM Provider (Anthropic / Ollama)**: Stateless compute layer for natural language generation.

## RAG Ingestion/Retrieval Flow
- **Ingestion**: Markdown -> Recursive Character Splitter -> `nomic-embed-text` -> pgvector `DocumentChunk`.
- **Retrieval**: User query -> `nomic-embed-text` -> pgvector L2 Distance search -> Top 5 chunks -> Injected into Agent Context.

## Database Schema
- **Session**: `id`, `title`, `created_at`, `updated_at`
- **Message**: `id`, `session_id`, `role`, `content`, `sources`, `created_at`
- **DocumentChunk**: `id`, `source_id`, `title`, `content`, `metadata`, `embedding`

## Security
- **Untrusted HTML**: Rendered via `<iframe sandbox="allow-scripts allow-same-origin">` or React-Markdown to prevent XSS.
- **Secrets**: Excluded via `.gitignore` and `.env.example`.

## Deployment Topology
- Local Docker container for PostgreSQL.
- Native Python process for FastAPI.
- Native Node process for Vite.
- Local Ollama daemon for embeddings and local LLM fallback.
