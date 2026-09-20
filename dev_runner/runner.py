from __future__ import annotations

import subprocess
import sys


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
        print()
        print("No automatic pull performed.")
    else:
        print("Remote status: Up to date")


if __name__ == "__main__":
    main()
