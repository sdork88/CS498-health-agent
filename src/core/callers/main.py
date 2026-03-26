import os
from dotenv import load_dotenv
from anthropic import Anthropic
from .models import BaseCaller

load_dotenv()


class ClaudeCaller(BaseCaller):
    """Single-turn streaming caller. No loop, no tool logic — just talks to Claude."""

    def __init__(self, system_message, model="claude-sonnet-4-6", max_tokens=16000,
                 thinking_budget=3000, tools=None):
        super().__init__(system_message, model, max_tokens)
        self.thinking_budget = thinking_budget
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tools = tools or []

    def call(self, messages,silent=False):
        """Stream one turn. Returns dict with text, thinking, citations, stop_reason, content."""
        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            thinking={"type": "enabled", "budget_tokens": self.thinking_budget},
            system=self.system_message,
            messages=messages,
        )
        if self.tools:
            kwargs["tools"] = self.tools

        text = ""
        thinking = ""
        citations = []

        with self.client.messages.stream(**kwargs) as stream:
            for event in stream:
                etype = getattr(event, "type", None)

                if etype == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta":
                        if not silent:
                            print(delta.text, end="", flush=True)
                        text += delta.text
                    elif delta.type == "thinking_delta":
                        thinking += delta.thinking

            final = stream.get_final_message()

        for block in final.content:
            if getattr(block, "type", None) == "text":
                for cite in getattr(block, "citations", []) or []:
                    url = getattr(cite, "url", "")
                    title = getattr(cite, "title", "")
                    if url and (title, url) not in citations:
                        citations.append((title, url))

        return {
            "text": text,
            "thinking": thinking,
            "citations": citations,
            "stop_reason": final.stop_reason,
            "content": final.content,
        }
