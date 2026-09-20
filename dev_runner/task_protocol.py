from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_OPERATIONS = {
    "RUN_TESTS",
    "GIT_STATUS",
    "GIT_DIFF",
    "CREATE_FILE",
    "UPDATE_FILE",
}


@dataclass
class QueueTask:
    task_id: str
    operation: str
    description: str
    requested_by: str = "chatgpt"
    metadata: dict[str, Any] | None = None

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")

        if self.operation not in ALLOWED_OPERATIONS:
            raise ValueError(
                f"Unsupported operation: {self.operation}. "
                f"Allowed operations: {sorted(ALLOWED_OPERATIONS)}"
            )

        if not self.description:
            raise ValueError("description is required")

        if self.metadata is None:
            self.metadata = {}
