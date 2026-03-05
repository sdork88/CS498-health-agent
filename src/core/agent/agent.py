

from .models import Agent, HealthUserInfoField

class HealthAgent(Agent):
    """Agent specialized for health users."""
    def __init__(self, name: str):
        super().__init__(name)

    def call(self, observation):
        # Implement health-specific call logic here
        pass

    def use_tool(self, tool_name, tool_input):
        # Implement health-specific tool usage here
        pass

    def update_user_memory(self, field: HealthUserInfoField, new_value):
        super().update_user_memory(field, new_value)