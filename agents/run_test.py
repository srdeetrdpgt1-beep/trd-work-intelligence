from agents.core.base import AgentContext
from agents.core.registry import AgentRegistry
from agents.test_agent import TestAgent


def main() -> None:
    registry = AgentRegistry()
    registry.register(TestAgent())

    context = AgentContext(correlation_id="TEST-001")

    agent = registry.get("test-agent")

    result = agent.run(
        {"message": "TRD system test"},
        context,
    )

    print("Registered agents:", registry.list_agents())
    print("Agent:", result.agent_name)
    print("Decision:", result.decision)
    print("Confidence:", result.confidence)
    print("Human review:", result.needs_human_review)
    print("Data:", result.data)


if __name__ == "__main__":
    main()
