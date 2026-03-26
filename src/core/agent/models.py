from enum import Enum, auto
from typing import List, Dict, Any
from core.agent.user_info.models import UserInfo, UserInfoField
from core.agent.user_info.health_user import HealthUser, HealthUserInfoField

class ConversationModel:
    """Stores and manages conversation history for the agent."""
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add_message(self, sender: str, message: str):
        self.history.append({"sender": sender, "message": message})

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history



class Agent:
    """Base agent with conversation and user info memory."""
    def __init__(self, name: str):
        self.name = name
        self.conversation = ConversationModel()
        self.user_info = HealthUser(name=name)

    def call(self, observation):
        raise NotImplementedError("Subclasses must implement this method")

    def use_tool(self, tool_name, tool_input):
        raise NotImplementedError("Subclasses must implement this method")

    def update_user_memory(self, field: HealthUserInfoField, new_value):
        """Update the user's memory object for a given field."""
        self.user_info.update_field(field, new_value)