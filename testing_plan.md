# Manual UI Test Plan

## Core Chat Functionality
1. **New Chat**: Click "New Chat". Ensure a new session appears in the sidebar and the chat window clears.
2. **Follow-up Question**: Ask "What are the core drivers of growth?" then ask "Can you give an example of the first one?". Verify the LLM maintains conversational context.

## RAG & Source Citations
1. **Source display**: Ask a specific question about Lenny's podcast (e.g. "What did Brian Chesky say about design?").
2. Verify the response includes inline citations (e.g. `[1]`).
3. Verify there is a citation list at the bottom matching the numbers.

## Provider Switching
1. Select "Ollama" in the provider dropdown. Ask a question and verify the response generates.
2. Select "Claude" in the provider dropdown. Ask a question and verify the response generates.
3. Remove the Anthropic API key from `.env`. Try using Claude. Verify a graceful error message is displayed in the UI.
4. Stop the Ollama daemon. Try using Ollama. Verify a graceful connection error is displayed.

## Skills & Artifacts
1. **Ship 30 for 30**: Select "Ship 30 for 30" in the skill dropdown, or click the Ship 30 quick action.
2. Ask "Write an essay about product market fit."
3. Verify the generated output is wrapped in a markdown artifact and the Artifact Viewer panel opens.
4. Verify the Artifact Viewer renders the markdown/HTML safely.
5. Inspect the Artifact Viewer in dev tools to ensure the `<iframe>` has proper `sandbox` attributes.
