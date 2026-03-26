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
                "enum": ["name", "age", "weight", "height", "medical_conditions", "allergies"],
                "description": "Which field to access (required for set/get)",
            },
            "value": {
                "description": "The value to store (required for set)",
            },
        },
        "required": ["action"],
    },
}

def get_all_schemas(allowed_domains=None, blocked_domains=None, web_search_max_uses=5):
    """Return the full list of tool schemas ready to pass to the Anthropic API."""
    return [
        HEALTH_MEMORY_SCHEMA,
    ]
