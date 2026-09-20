from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AIResponse:
    provider: str
    model: str
    content: dict[str, Any]
    raw_response: Any = None


class AIProvider(ABC):
    """
    Common interface for all AI providers.

    Agents depend on this interface, not on a specific AI vendor.
    """

    name: str = "base-provider"
    version: str = "0.1.0"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        response_schema: dict[str, Any] | None = None,
    ) -> AIResponse:
        raise NotImplementedError
