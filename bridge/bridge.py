from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = BASE_DIR / "dev_runner" / "tasks" / "inbox"
RESULTS_DIR = BASE_DIR / "dev_runner" / "tasks" / "results"

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
        stdout=sys.stderr,
    )


def read_result(task_id: str) -> dict:
    result_path = RESULTS_DIR / f"{task_id}.json"

    if not result_path.exists():
        raise FileNotFoundError(
            f"Result not found for task: {task_id}"
        )

    with result_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def handle_request(task: dict) -> dict:
    task_path = submit_task(task)
    run_runner()
    result = read_result(task["task_id"])

    return {
        "task_path": str(task_path),
        "result": result,
    }


def main() -> None:
    request = json.load(sys.stdin)

    try:
        response = handle_request(request)
        print(json.dumps(response))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": str(exc),
                }
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
