from __future__ import annotations

import subprocess
import sys

from dev_runner.protocol import DevelopmentResult, DevelopmentTask, TestResult


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
            f"Unable to compare local and remote commits:\n"
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


def main() -> None:
    print("=== TRD Development Runner ===")
    print()

    task = DevelopmentTask(
        task_id="DEV-RUNNER-001",
        description="Run the TRD development test suite",
    )

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
    print("Executing task:", task.task_id)

    result = execute_task(task)

    print()
    print("=== DEVELOPMENT RESULT ===")
    print("Task ID:", result.task_id)
    print("Status:", result.status)

    if result.test_result is not None:
        print("Command:", " ".join(result.test_result.command))
        print("Exit code:", result.test_result.exit_code)

        if result.test_result.stdout:
            print()
            print("Output:")
            print(result.test_result.stdout)

        if result.test_result.stderr:
            print()
            print("Errors:")
            print(result.test_result.stderr)

    if result.error:
        print("Error:", result.error)

    print()
    print("=== END ===")


if __name__ == "__main__":
    main()
