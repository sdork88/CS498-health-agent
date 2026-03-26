from core.callers.main import ClaudeCaller

GUIDELINES_OK = "GUIDELINES_OK"

class OrchestrateAgent:
    """Generic agentic loop. Plug in any agent that implements the agent interface."""

    def __init__(self, agent, recommender=None, verifier=None):
        self.agent = agent
        self.recommender = recommender
        self.verifier = verifier
        self.caller = ClaudeCaller(
            system_message=agent.system_message,
            tools=agent.tools,
        )

    def run(self, observation):
        context = self._build_context(observation)
        messages = [{"role": "user", "content": context}]

        thinking = ""
        response = ""
        citations = []

        # Run silently — hold output until after guidelines check
        silent = self.verifier is not None
        while True:
            result = self.caller.call(messages, silent=silent)
            thinking = result["thinking"]
            response += result["text"]
            citations = result["citations"]

            if result["stop_reason"] != "tool_use":
                break

            tool_results = [
                r for block in result["content"]
                if (r := self.agent.dispatch_tool(block)) is not None
            ]
            messages.append({"role": "assistant", "content": result["content"]})
            messages.append({"role": "user", "content": tool_results})


        # Now print the verified final response
        print(response, flush=True)
        self.agent.display_citations(citations)

        self.agent.conversation.add_message("user", observation)
        self.agent.conversation.add_message("assistant", response)
        return {"thinking": thinking, "response": response, "citations": citations}

    def _build_context(self, observation: str) -> str:
        parts = []

        if hasattr(self.agent, "context_for"):
            parts.append(self.agent.context_for(observation))
        else:
            parts.append(observation)

        if self.recommender and hasattr(self.agent, "user_info"):
            neighbours = self.recommender.recommend(self._user_profile_dict())
            if neighbours:
                recs = "\n".join(
                    f"  {i+1}. [{n['fitness_type']} / {n['fitness_goal']}] "
                    f"Exercises: {n['exercises']}. Diet: {n['diet'][:120]}…"
                    for i, n in enumerate(neighbours)
                )
                parts.append(
                    f"[Similar user recommendations from dataset — use as supporting reference]\n{recs}"
                )

        return "\n\n".join(parts)       


    def _user_profile_dict(self) -> dict:
        """Extract a plain dict from the agent's user_info for tools that need it."""
        ui = getattr(self.agent, "user_info", None)
        if ui is None:
            return {}
        return {
            "age":          getattr(ui, "age", None),
            "height":       getattr(ui, "height", None),
            "weight":       getattr(ui, "weight", None),
            "sex":          getattr(ui, "sex", None),
            "hypertension": next((c for c in (getattr(ui, "medical_conditions", None) or [])
                                  if "hypertension" in c.lower()), None),
            "diabetes":     next((c for c in (getattr(ui, "medical_conditions", None) or [])
                                  if "diabetes" in c.lower()), None),
            "fitness_goal": getattr(ui, "fitness_goal", None),
        }
