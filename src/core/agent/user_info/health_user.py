from enum import Enum, auto
from typing import List
from core.agent.user_info.models import UserInfo, UserInfoField

class HealthUserInfoField(Enum):
    WEIGHT = auto()
    HEIGHT = auto()
    MEDICAL_CONDITIONS = auto()
    ALLERGIES = auto()

class HealthUser(UserInfo):
    """Represents a user with health attributes, built on UserInfo."""
    def __init__(self, name: str = "", email: str = "", age: int = None, weight: float = None, height: float = None, medical_conditions: List[str] = None, allergies: List[str] = None, sex: str = None, fitness_goal: str = None):
        super().__init__(name, email, age)
        self.weight = weight
        self.height = height
        self.medical_conditions = medical_conditions or []
        self.allergies = allergies or []
        self.sex = sex
        self.fitness_goal = fitness_goal

    def update_field(self, field, value):
        if isinstance(field, UserInfoField):
            super().update_field(field, value)
        elif isinstance(field, HealthUserInfoField):
            if field == HealthUserInfoField.WEIGHT:
                self.weight = value
            elif field == HealthUserInfoField.HEIGHT:
                self.height = value
            elif field == HealthUserInfoField.MEDICAL_CONDITIONS:
                self.medical_conditions = value
            elif field == HealthUserInfoField.ALLERGIES:
                self.allergies = value
            else:
                raise ValueError(f"Unknown health field: {field}")
        else:
            raise ValueError(f"Unknown field type: {field}")
