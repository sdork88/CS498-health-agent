from core.agent.models import Agent
from core.agent.user_info.health_user import HealthUser
from tools.health_memory import HealthMemoryTool
from tools.fitness_recommender import FitnessRecommender
from tools.definitions import get_all_schemas, DEFAULT_HEALTH_DOMAINS

LABEL_UPDATED = "Updated profile"
LABEL_RETRIEVED = "Retrieved profile"
LABEL_SEARCH = "Searching verified sources"
LABEL_KNN = "Finding similar users"


class HealthAgent(Agent):
    """Health-specific agent. Owns its system message, tools, and tool dispatch."""

    def __init__(self, name, allowed_domains=None):
        super().__init__(name)
        user = HealthUser(name=name)
        self.user_info = user
        self.health_memory = HealthMemoryTool(user)
        self.tools = get_all_schemas(allowed_domains=allowed_domains or DEFAULT_HEALTH_DOMAINS)

    @property
    def system_message(self):
        profile = self.health_memory.execute({"action": "get_all"})
        profile_str = ", ".join(f"{k}: {v}" for k, v in profile.items() if v)
        base = "You are a supportive health and fitness coach."
        if profile_str:
            return (
                f"{base} Current user profile: {profile_str}. "
                "Use health_memory to save any health details the user mentions. "
                "Use fitness_recommender to find similar users and reference their plans. "
                "Use web search to find verified health information when needed."
            )
        return (
            f"{base} Use health_memory to save health details as the user shares them. "
            "Use fitness_recommender to find similar users and reference their plans. "
            "Use web search to find verified health information when needed."
        )

    def context_for(self, observation):
        health_data = self.health_memory.execute({"action": "get_all"})
        return f"[User health profile: {health_data}]\n\n{observation}"

    def display_citations(self, citations):
        if citations:
            print("\n  Sources:")
            for title, url in citations:
                print(f"    - {title or url}: {url}", flush=True)

    def dispatch_tool(self, block):
        """Execute a tool_use block. Returns a tool_result dict, or None if unhandled."""
        name = getattr(block, "name", None)
        btype = getattr(block, "type", None)

        if btype == "tool_use" and name == "health_memory":
            result = self.health_memory.execute(block.input)
            action = block.input.get("action", "")
            label = LABEL_UPDATED if action == "set" else LABEL_RETRIEVED
            field = block.input.get("field", "profile")
            print(f"\n  [{label}: {field}]", flush=True)
            return {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}

        if btype == "tool_use" and name == "fitness_recommender":
            print(f"\n  [{LABEL_KNN}...]", flush=True)
            recommender = FitnessRecommender.get()
            if recommender:
                neighbours = recommender.recommend(block.input)
                content = "\n".join(
                    f"{i+1}. [{n['fitness_type']} / {n['fitness_goal']}] "
                    f"Exercises: {n['exercises']}. Equipment: {n['equipment']}. "
                    f"Diet: {n['diet']}. Recommendation: {n['recommendation'][:300]}…"
                    for i, n in enumerate(neighbours)
                )
            else:
                content = "Fitness recommender model not loaded."
            return {"type": "tool_result", "tool_use_id": block.id, "content": content}

        if btype in ("server_tool_use", "tool_use") and name == "web_search":
            print(f"\n  [{LABEL_SEARCH}...]", flush=True)
            return None  # handled server-side

        return None
