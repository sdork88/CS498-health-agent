"""All tool schemas in one place — feed directly into the Anthropic API."""

DEFAULT_HEALTH_DOMAINS = [
    "nih.gov", "cdc.gov", "mayoclinic.org", "healthline.com",
    "webmd.com", "medlineplus.gov", "nutrition.gov", "nhs.uk",
]

HEALTH_MEMORY_SCHEMA = {
    "name": "health_memory",
    "description": (
        "Store or retrieve user health information. "
        "Call this whenever the user mentions their name, age, weight, height, "
        "medical conditions, or allergies so the information is saved to their profile."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["set", "get", "get_all"],
                "description": "set to save a value, get to retrieve one field, get_all to retrieve the full profile",
            },
            "field": {
                "type": "string",
                "enum": ["name", "age", "weight", "height", "medical_conditions", "allergies", "sex", "fitness_goal"],
                "description": "Which field to access (required for set/get)",
            },
            "value": {
                "description": "The value to store (required for set)",
            },
        },
        "required": ["action"],
    },
}
def web_search_schema(allowed_domains=None, blocked_domains=None, max_uses=5):
    schema = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_uses,
    }
    if allowed_domains:
        schema["allowed_domains"] = allowed_domains
    elif blocked_domains:
        schema["blocked_domains"] = blocked_domains
    return schema

FITNESS_RECOMMENDER_SCHEMA = {
    "name": "fitness_recommender",
    "description": (
        "Find 5 users from the gym recommendation dataset with similar profiles and return "
        "their workout and diet recommendations. Call this when the user asks for a workout "
        "plan, exercise recommendations, or diet advice. All fields are optional — any missing "
        "values will be imputed from the dataset."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "age":          {"type": "number",  "description": "User age in years"},
            "height":       {"type": "number",  "description": "Height in meters"},
            "weight":       {"type": "number",  "description": "Weight in kg"},
            "sex":          {"type": "string",  "enum": ["male", "female"], "description": "Biological sex"},
            "hypertension": {"type": "string",  "enum": ["yes", "no"]},
            "diabetes":     {"type": "string",  "enum": ["yes", "no"]},
            "fitness_goal": {"type": "string",  "description": "e.g. weight loss, weight gain, muscle gain"},
        },
    },
}


def get_all_schemas(allowed_domains=None, blocked_domains=None, web_search_max_uses=5):
    """Return the full list of tool schemas ready to pass to the Anthropic API."""
    return [
        web_search_schema(allowed_domains=allowed_domains, blocked_domains=blocked_domains, max_uses=web_search_max_uses),
        HEALTH_MEMORY_SCHEMA,
        FITNESS_RECOMMENDER_SCHEMA,
    ]
