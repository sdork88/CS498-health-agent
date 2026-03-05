

class BaseCaller:
    def __init__(self, system_message, model, max_tokens=1024, temperature=0.7, agent=None):
        self.system_message = system_message
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.agent = agent  # Optionally link to agent for conversation/user info

    def call(self, prompt):
        # Optionally add prompt to agent's conversation
        if self.agent:
            self.agent.conversation.add_message("user", prompt)
        raise NotImplementedError("Subclasses must implement this method")