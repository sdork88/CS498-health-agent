from core.agent.user_info.health_user import HealthUser


class HealthMemoryTool:
    """Manages user health profile — get/set individual fields or the full profile."""

    name = "health_memory"

    def __init__(self,user: HealthUser):
        self.user = user

    def execute(self,input_data):
        action =input_data.get("action", "get")
        field =input_data.get("field")

        if action == "get_all":
            return {
                "name":self.user.name,
                "email": self.user.email,
                "age": self.user.age,
                "weight": self.user.weight,
                "height": self.user.height,
                "medical_conditions": self.user.medical_conditions,
                "allergies": self.user.allergies,
            }
        elif action == "get":
            return self._get(field)
        elif action == "set":
            return self._set(field, input_data.get("value"))
        else:
            return {"error": f"Unknown action: {action}"}

    def _get(self, field):
        value = getattr(self.user, field, None)
        if value is None and field not in ("name", "email", "age", "weight", "height",
                                           "medical_conditions", "allergies", "sex", "fitness_goal"):
            return {"error": f"Unknown field: {field}"}
        return {"field": field, "value": value}

    def _set(self, field, value):
        try:
            if field =="weight":
                self.user.weight = float(value)
            elif field == "height":
                self.user.height = float(value)
            elif field =="age":
                self.user.age = int(value)
            elif field in ("medical_conditions","allergies"):
                setattr(self.user, field, value if isinstance(value, list) else [value])
            elif field in ("name", "email", "sex", "fitness_goal"):
                setattr(self.user, field, str(value))
            else:
                return {"error": f"Unknown field: {field}"}
            return {"success": True, "field": field, "value": getattr(self.user, field)}
        except (ValueError, TypeError) as e:
            return {"error":f"Invalid value for {field}: {e}"}
