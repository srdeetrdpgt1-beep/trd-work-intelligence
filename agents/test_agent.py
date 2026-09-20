from agents.core.base import Agent, AgentContext, AgentResult


class TestAgent(Agent):
    name = "test-agent"
    version = "0.1.0"

    def run(
        self,
        input_data: dict,
        context: AgentContext,
    ) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            decision="TEST_OK",
            confidence=1.0,
            needs_human_review=False,
            data={"echo": input_data},
            evidence_refs=[],
        )
