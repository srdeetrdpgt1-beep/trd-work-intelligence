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


if __name__ == "__main__":
    main()
