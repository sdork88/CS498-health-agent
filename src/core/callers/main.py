import os
from anthropic import Anthropic
from .models import BaseCaller


class ClaudeCaller(BaseCaller):
    def __init__(self, system_message, model="claude-3-5-sonnet-20241022", max_tokens=1024, temperature=0.7, agent=None):
        super().__init__(system_message, model, max_tokens, temperature, agent=agent)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def call(self, user_input):
        # Add user input to agent's conversation if agent is provided
        if self.agent:
            self.agent.conversation.add_message("user", user_input)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_message,
            messages=[
                {"role": "user", "content": user_input}
            ]
        )
        # Add response to agent's conversation
        if self.agent:
            self.agent.conversation.add_message("assistant", response.content[0].text)
        return response.content[0].text