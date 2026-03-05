
from enum import Enum, auto


class UserInfoField(Enum):
    NAME = auto()
    EMAIL = auto()
    AGE = auto()

class UserInfo:
    """Abstracted user info with base attributes."""
    def __init__(self, name: str = "", email: str = "", age: int = None):
        self.name = name
        self.email = email
        self.age = age

    def update_field(self, field: UserInfoField, value):
        if field == UserInfoField.NAME:
            self.name = value
        elif field == UserInfoField.EMAIL:
            self.email = value
        elif field == UserInfoField.AGE:
            self.age = value
        else:
            raise ValueError(f"Unknown field: {field}")