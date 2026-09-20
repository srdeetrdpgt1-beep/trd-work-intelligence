from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    correlation_id: str
    environment: str = "development"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_name: str
    decision: str
    confidence: float
    needs_human_review: bool
    data: dict[str, Any] = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)


class Agent(ABC):
    """
    Common interface for every agent in the system.

    Agents should:
    - receive structured input
    - return structured output
    - avoid direct database mutation
    - avoid hidden side effects
    - be independently replaceable
    """

    name: str = "base-agent"
    version: str = "0.1.0"

    @abstractmethod
    def run(
        self,
        input_data: dict[str, Any],
        context: AgentContext,
    ) -> AgentResult:
        raise NotImplementedError
