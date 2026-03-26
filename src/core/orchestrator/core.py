from core.callers.main import ClaudeCaller


class OrchestrateAgent:
    """Generic agentic loop. Plug in any agent that implements the agent interface."""

    def __init__(self, agent):
        self.agent = agent
        self.caller = ClaudeCaller(
            system_message=agent.system_message,
            tools=agent.tools,
        )

    def run(self, observation):
        context = self.agent.context_for(observation) if hasattr(self.agent, "context_for") else observation
        messages = [{"role": "user", "content": context}]

        thinking = ""
        response = ""
        citations = []

        while True:
            result = self.caller.call(messages)
            thinking = result["thinking"]
            response += result["text"]
            citations = result["citations"]

            if result["stop_reason"] != "tool_use":
                print()
                self.agent.display_citations(citations)
                break

            tool_results = [
                r for block in result["content"]
                if (r := self.agent.dispatch_tool(block)) is not None
            ]
            messages.append({"role": "assistant", "content": result["content"]})
            messages.append({"role": "user", "content": tool_results})

        self.agent.conversation.add_message("user", observation)
        self.agent.conversation.add_message("assistant", response)
        return {"thinking": thinking, "response": response, "citations": citations}
