"""Base agent class for the PM Agent Suite."""

from anthropic import Anthropic
from typing import Optional


class BaseAgent:
    """
    Importable base class for all PM agents.
    Subclass this and set `name`, `description`, and `system_prompt`.
    """

    name: str = "Base Agent"
    description: str = "A generic program management agent."
    icon: str = "◎"
    system_prompt: str = "You are a helpful program management assistant."

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)   # falls back to ANTHROPIC_API_KEY env var
        self.model = model
        self.history: list[dict] = []

    def chat(self, user_message: str, stream: bool = False) -> str:
        """
        Send a message to the agent and return its response.
        Maintains conversation history automatically.

        Args:
            user_message: The message to send.
            stream:        If True, print streamed tokens and return full text.

        Returns:
            The agent's response as a string.
        """
        self.history.append({"role": "user", "content": user_message})

        if stream:
            response_text = self._stream(self.history)
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.system_prompt,
                messages=self.history,
            )
            response_text = response.content[0].text

        self.history.append({"role": "assistant", "content": response_text})
        return response_text

    def _stream(self, messages: list[dict]) -> str:
        full_text = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_text += text
        print()
        return full_text

    def reset(self):
        """Clear conversation history."""
        self.history = []

    def get_history(self) -> list[dict]:
        """Return a copy of the conversation history."""
        return list(self.history)

    def __repr__(self):
        return f"<{self.__class__.__name__} turns={len(self.history) // 2}>"
