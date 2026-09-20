from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = BASE_DIR / "dev_runner" / "tasks" / "inbox"

ALLOWED_OPERATIONS = {
    "RUN_TESTS",
    "GIT_STATUS",
    "GIT_DIFF",
    "CREATE_FILE",
    "UPDATE_FILE",
    "APPLY_PATCH",
    "APPLY_PATCH_AND_TEST",
}


def submit_task(task: dict) -> Path:
    task_id = task.get("task_id")
    operation = task.get("operation")
    description = task.get("description")

    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id is required")

    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(f"Unsupported operation: {operation}")

    if not isinstance(description, str) or not description:
        raise ValueError("description is required")

    task.setdefault("requested_by", "chatgpt")
    task.setdefault("metadata", {})

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    task_path = INBOX_DIR / f"{task_id}.json"

    if task_path.exists():
        raise FileExistsError(f"Task already exists: {task_id}")

    with task_path.open("w", encoding="utf-8") as handle:
        json.dump(task, handle, indent=2)

    return task_path


def run_runner() -> None:
    subprocess.run(
        [sys.executable, "-m", "dev_runner.runner"],
        cwd=BASE_DIR,
        check=True,
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m bridge.bridge '<task-json>'"
        )

    task = json.loads(sys.argv[1])
    task_path = submit_task(task)

    print(f"TASK_SUBMITTED: {task_path}")

    run_runner()


if __name__ == "__main__":
    main()
