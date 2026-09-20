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
    print("Python:")
    print(sys.version.split()[0])
    print()
    print("Checking GitHub...")
    print(
        "Remote status:",
        "NEW COMMITS AVAILABLE" if remote_is_ahead() else "Up to date",
    )


if __name__ == "__main__":
    main()
