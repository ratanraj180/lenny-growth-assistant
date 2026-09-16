# Product Requirements Document (PRD)

## User
Growth practitioners, product managers, and founders seeking advice derived from Lenny Rachitsky's podcast and newsletters.

## Problem
Searching through hundreds of hours of podcasts and long-form newsletters to find specific, actionable growth advice is time-consuming and often imprecise.

## Success Metric
- 100% of answers are grounded in the actual transcript dataset (no hallucination).
- The Ship 30 for 30 skill successfully generates structured 1,250-word essays based on context.
- High system availability and graceful error handling when LLM providers are down.

## Assumptions
- Users have local compute sufficient for Ollama (Llama 3) if they choose not to use the Claude Cloud API.
- The `lennys-newsletterpodcastdata` repository remains available and parseable.

## Scope
- Conversational chat interface with history.
- Model selector (Cloud vs Local).
- Dedicated Ship 30 for 30 skill.
- Artifact generation and secure rendering.
- RAG pipeline utilizing pgvector.

## User Flows
1. **New Session**: User opens app, sees an empty chat, clicks "New Chat", and selects a provider.
2. **Q&A**: User asks a question -> Backend embeds query -> Retrieves context -> LLM generates answer -> Citations are displayed.
3. **Artifact Generation**: User asks for an essay -> LLM formats as markdown artifact -> Frontend renders in secure viewer.

## Acceptance Criteria
- [x] Backend runs FastAPI and uses Postgres for storage.
- [x] Transcripts are embedded and stored in pgvector.
- [x] Agent refuses to answer if out of context.
- [x] Ollama fallback works flawlessly.
- [x] HTML artifacts are sandboxed.

## Risks & Trade-offs
- **Risk**: Local LLMs (Ollama) may be too slow or hallucinate more than Claude.
- **Trade-off**: Used a synchronous agent processing loop for simplicity instead of SSE streaming, which means slightly higher latency for the user but significantly simpler state management.
