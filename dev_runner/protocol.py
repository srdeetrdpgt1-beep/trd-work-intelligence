from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DevelopmentTask:
    task_id: str
    description: str
    requested_by: str = "chatgpt"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.exit_code == 0


@dataclass
class DevelopmentResult:
    task_id: str
    status: str
    test_result: TestResult | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
