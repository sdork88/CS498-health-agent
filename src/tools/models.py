
# For future tool integration with agent/user info
from ..core.agent.models import HealthUserInfoField



class Itool:
    """Interface for tools that can be used by the agent."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, input_data):
        """Execute the tool with the given input data."""
        raise NotImplementedError("Subclasses must implement this method")