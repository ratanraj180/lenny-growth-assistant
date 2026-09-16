# Design Principles & Architecture

## UI/UX Principles
- **Clarity over Clutter**: Focus on the conversation. The UI should resemble leading AI tools (ChatGPT, Claude) with a clean sidebar and main chat area.
- **Transparency**: Always show where the AI got its information. Citations are non-negotiable.
- **Security First**: The Artifact Viewer must never blindly trust HTML.

## Information Architecture
- **Sidebar**: Session history, "New Chat" button, Provider/Model toggle.
- **Main Chat**: Message history, input box, "Ship 30 for 30" quick action button.
- **Right Panel (Artifact Viewer)**: Expands when an artifact is generated.

## Interaction States
- **Loading**: Pulse animations or spinners while waiting for the LLM.
- **Error**: Inline red alerts with clear error messages (e.g., "Ollama is not running" or "API Key missing").

## Accessibility
- High contrast text.
- Semantic HTML (using proper `main`, `aside`, `nav` tags).
- Keyboard navigable chat input.
