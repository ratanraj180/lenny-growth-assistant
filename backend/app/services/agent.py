import os
import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
import ollama
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self, provider_name: str):
        self.provider_name = provider_name.lower()
        if self.provider_name == "claude":
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("Anthropic API key is missing. Claude will fail if called.")
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = "claude-3-haiku-20240307" # Using haiku for speed/demo
        elif self.provider_name == "ollama":
            self.model = "llama3.2:1b" # Using a blazing fast 1B parameter model
        else:
            raise ValueError(f"Unknown provider {provider_name}")

    def generate(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        try:
            if self.provider_name == "claude":
                if not settings.ANTHROPIC_API_KEY:
                    raise Exception("ANTHROPIC_API_KEY is not set.")
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text
            elif self.provider_name == "ollama":
                # Convert system prompt to a message for Ollama if needed, though ollama SDK supports system messages in format
                ollama_messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
                ollama_messages.extend(messages)
                
                response = ollama.chat(
                    model=self.model,
                    messages=ollama_messages
                )
                return response['message']['content']
        except Exception as e:
            logger.error(f"LLM Provider Error ({self.provider_name}): {e}")
            raise Exception(f"Failed to generate response using {self.provider_name}. {str(e)}")

from app.services.retrieval import search_transcripts
from app.core.database import SessionLocal

class Agent:
    def __init__(self, provider_name: str = "ollama"):
        self.provider = LLMProvider(provider_name)
    
    def process_message(self, query: str, history: List[Dict[str, str]], skill: str = None) -> Dict[str, Any]:
        """
        Process a user message, retrieve context, and generate a response.
        """
        db = SessionLocal()
        context_chunks = []
        try:
            # Only retrieve if we have a real question, but for simplicity we do it always
            context_chunks = search_transcripts(query, db, limit=5)
        except Exception as e:
            logger.warning(f"Retrieval failed or DB not available: {e}")
        finally:
            db.close()

        context_text = ""
        sources = []
        if context_chunks:
            for idx, chunk in enumerate(context_chunks):
                sources.append({"id": idx+1, "source_id": chunk["source_id"], "title": chunk["title"]})
                context_text += f"\n--- Source [{idx+1}]: {chunk['title']} ({chunk['source_id']}) ---\n{chunk['content']}\n"
        
        system_prompt = (
            "You are the Lenny Growth Assistant, an AI expert based on Lenny Rachitsky's podcast and newsletter.\n"
            "Answer the user's questions strictly using the retrieved context provided below.\n"
            "If the context does not contain the answer, say 'I don't have enough information in my knowledge base to answer that.' DO NOT hallucinate.\n"
            "When using information from the context, include inline citations like [1], [2], etc., matching the source numbers.\n"
            "Your output can include markdown.\n\n"
            f"=== RETRIEVED CONTEXT ===\n{context_text}\n==========================\n"
        )
        
        if skill == "ship30":
            system_prompt += (
                "\n\n*** SHIP 30 FOR 30 SKILL ACTIVATED ***\n"
                "The user has requested a Ship 30 for 30 style essay. Instead of a standard chat response, you must write a comprehensive essay.\n"
                "Requirements:\n"
                "- Length: Approximately 1,250 words.\n"
                "- Strong hook at the beginning.\n"
                "- Clear narrative progression.\n"
                "- Use headings and bullets where useful.\n"
                "- Selective bold emphasis for key points.\n"
                "- Specific actionable takeaways.\n"
                "- The claims MUST be grounded in the provided Lenny transcripts.\n"
                "Output the essay formatted entirely in a markdown artifact block like this:\n"
                "```artifact\n# [Essay Title]\n[Essay Content]\n```\n"
            )
        
        # Prepare messages
        messages = history[-5:] # keep last 5 for context
        messages.append({"role": "user", "content": query})
        
        try:
            response_text = self.provider.generate(messages, system_prompt=system_prompt)
        except Exception as e:
            response_text = f"An error occurred while generating the response: {e}"
        
        return {
            "role": "assistant",
            "content": response_text,
            "sources": sources
        }

