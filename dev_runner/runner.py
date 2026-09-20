from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from dev_runner.protocol import DevelopmentResult, DevelopmentTask, TestResult
from dev_runner.task_protocol import QueueTask


BASE_DIR = Path(__file__).resolve().parent
INBOX_DIR = BASE_DIR / "tasks" / "inbox"
COMPLETED_DIR = BASE_DIR / "tasks" / "completed"
RESULTS_DIR = BASE_DIR / "tasks" / "results"
REPOSITORY_ROOT = BASE_DIR.parent


def validate_repository_path(relative_path: str) -> Path:
    if not relative_path:
        raise ValueError("file path is required")

    candidate = (REPOSITORY_ROOT / relative_path).resolve()
    repository_root = REPOSITORY_ROOT.resolve()

    try:
        candidate.relative_to(repository_root)
    except ValueError as exc:
        raise ValueError(
            f"Path is outside repository: {relative_path}"
        ) from exc

    if ".git" in candidate.relative_to(repository_root).parts:
        raise ValueError("Modifying .git paths is not permitted")

    return candidate


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout.strip()
    error = result.stderr.strip()

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n{error}"
        )

    return output


def remote_is_ahead() -> bool:
    run(["git", "fetch", "origin", "main"])

    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD..origin/main"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Unable to compare local and remote commits:\n"
            f"{result.stderr.strip()}"
        )

    return int(result.stdout.strip()) > 0


def pull_remote_changes() -> str:
    return run(["git", "pull", "--ff-only", "origin", "main"])


def run_tests() -> TestResult:
    command = ["python", "-m", "agents.run_test"]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    return TestResult(
        command=command,
        exit_code=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def save_task_result(task_path: Path, result_payload: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)

    task_id = result_payload.get("task_id", task_path.stem)
    result_path = RESULTS_DIR / f"{task_id}.json"

    with result_path.open("w", encoding="utf-8") as handle:
        json.dump(result_payload, handle, indent=2)

    completed_path = COMPLETED_DIR / task_path.name
    shutil.move(str(task_path), str(completed_path))


def save_task_error(task_path: Path, error: Exception) -> dict:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)

    result_payload = {
        "task_id": task_path.stem,
        "status": "ERROR",
        "error": str(error),
    }

    result_path = RESULTS_DIR / f"{task_path.stem}.json"
    with result_path.open("w", encoding="utf-8") as handle:
        json.dump(result_payload, handle, indent=2)

    completed_path = COMPLETED_DIR / task_path.name
    shutil.move(str(task_path), str(completed_path))

    return result_payload


def execute_task(task: DevelopmentTask) -> DevelopmentResult:
    try:
        test_result = run_tests()

        return DevelopmentResult(
            task_id=task.task_id,
            status="PASSED" if test_result.passed else "FAILED",
            test_result=test_result,
        )

    except Exception as exc:
        return DevelopmentResult(
            task_id=task.task_id,
            status="ERROR",
            error=str(exc),
        )


def process_queue_task(task_path: Path) -> dict:
    with task_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    task = QueueTask(
        task_id=payload.get("task_id", ""),
        operation=payload.get("operation", ""),
        description=payload.get("description", ""),
        requested_by=payload.get("requested_by", "unknown"),
        metadata=payload.get("metadata"),
    )

    task.validate()

    if task.operation == "GIT_STATUS":
        result = run(["git", "status", "--short"])

        result_payload = {
            "task_id": task.task_id,
            "status": "PASSED",
            "operation": "GIT_STATUS",
            "git_status": result,
        }

        save_task_result(task_path, result_payload)

        return result_payload

    if task.operation == "GIT_DIFF":
        result = run(["git", "diff", "--"])

        result_payload = {
            "task_id": task.task_id,
            "status": "PASSED",
            "operation": "GIT_DIFF",
            "git_diff": result,
        }

        save_task_result(task_path, result_payload)

        return result_payload

    if task.operation == "CREATE_FILE":
        metadata = task.metadata or {}

        file_path = metadata.get("file_path")
        content = metadata.get("content")

        if not isinstance(file_path, str):
            raise ValueError("CREATE_FILE requires metadata.file_path")

        if not isinstance(content, str):
            raise ValueError("CREATE_FILE requires metadata.content")

        target_path = validate_repository_path(file_path)

        if target_path.exists():
            raise FileExistsError(
                f"File already exists: {file_path}"
            )

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")

        result_payload = {
            "task_id": task.task_id,
            "status": "PASSED",
            "operation": "CREATE_FILE",
            "file_path": file_path,
        }

        save_task_result(task_path, result_payload)

        return result_payload

    if task.operation == "UPDATE_FILE":
        metadata = task.metadata or {}

        file_path = metadata.get("file_path")
        content = metadata.get("content")

        if not isinstance(file_path, str):
            raise ValueError("UPDATE_FILE requires metadata.file_path")

        if not isinstance(content, str):
            raise ValueError("UPDATE_FILE requires metadata.content")

        target_path = validate_repository_path(file_path)

        if not target_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not target_path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        target_path.write_text(content, encoding="utf-8")

        result_payload = {
            "task_id": task.task_id,
            "status": "PASSED",
            "operation": "UPDATE_FILE",
            "file_path": file_path,
        }

        save_task_result(task_path, result_payload)

        return result_payload

    if task.operation == "APPLY_PATCH":
        metadata = task.metadata or {}

        file_path = metadata.get("file_path")
        expected_content = metadata.get("expected_content")
        replacement_content = metadata.get("replacement_content")

        if not isinstance(file_path, str):
            raise ValueError("APPLY_PATCH requires metadata.file_path")

        if not isinstance(expected_content, str):
            raise ValueError(
                "APPLY_PATCH requires metadata.expected_content"
            )

        if not isinstance(replacement_content, str):
            raise ValueError(
                "APPLY_PATCH requires metadata.replacement_content"
            )

        target_path = validate_repository_path(file_path)

        if not target_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not target_path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        current_content = target_path.read_text(encoding="utf-8")
        match_count = current_content.count(expected_content)

        if match_count == 0:
            raise ValueError(
                f"Expected content was not found in: {file_path}"
            )

        if match_count > 1:
            raise ValueError(
                f"Expected content matched {match_count} times in: {file_path}; "
                "patch is ambiguous"
            )

        target_path.write_text(
            current_content.replace(
                expected_content,
                replacement_content,
                1,
            ),
            encoding="utf-8",
        )

        result_payload = {
            "task_id": task.task_id,
            "status": "PASSED",
            "operation": "APPLY_PATCH",
            "file_path": file_path,
        }

        save_task_result(task_path, result_payload)

        return result_payload

    if task.operation != "RUN_TESTS":
        raise ValueError(
            f"Operation not permitted: {task.operation}"
        )

    development_task = DevelopmentTask(
        task_id=task.task_id,
        description=task.description,
        requested_by=task.requested_by,
        metadata=task.metadata or {},
    )

    result = execute_task(development_task)

    result_payload = {
        "task_id": result.task_id,
        "status": result.status,
        "error": result.error,
        "test_result": None,
    }

    if result.test_result is not None:
        result_payload["test_result"] = {
            "command": result.test_result.command,
            "exit_code": result.test_result.exit_code,
            "passed": result.test_result.passed,
            "stdout": result.test_result.stdout,
            "stderr": result.test_result.stderr,
        }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)

    result_path = RESULTS_DIR / f"{task.task_id}.json"

    with result_path.open("w", encoding="utf-8") as handle:
        json.dump(result_payload, handle, indent=2)

    completed_path = COMPLETED_DIR / task_path.name
    shutil.move(str(task_path), str(completed_path))

    return result_payload


def process_pending_tasks() -> list[dict]:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    task_files = sorted(INBOX_DIR.glob("*.json"))

    results = []

    for task_path in task_files:
        try:
            results.append(process_queue_task(task_path))
        except Exception as exc:
            results.append(save_task_error(task_path, exc))

    return results


def main() -> None:
    print("=== TRD Development Runner ===")
    print()

    print("Branch:")
    print(run(["git", "branch", "--show-current"]))
    print()

    print("Git status:")
    print(run(["git", "status", "--short"]) or "Clean")
    print()

    print("Latest commit:")
    print(run(["git", "log", "-1", "--oneline"]))
    print()

    print("Checking GitHub...")

    if remote_is_ahead():
        print("Remote status: NEW COMMITS AVAILABLE")
        print("No automatic pull performed.")
    else:
        print("Remote status: Up to date")

    print()
    print("Checking development task queue...")

    results = process_pending_tasks()

    if not results:
        print("Queue status: No pending tasks")
    else:
        print(f"Processed tasks: {len(results)}")

        for result in results:
            print()
            print(json.dumps(result, indent=2))

    print()
    print("=== END ===")


if __name__ == "__main__":
    main()
