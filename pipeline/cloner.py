from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def clone_repository(repo_url: str, destination: str | Path) -> Path:
    """Clone a target repository into a clean destination directory."""
    target_path = Path(destination).resolve()
    if target_path.exists():
        shutil.rmtree(target_path)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target_path)],
        check=True,
    )
    return target_path


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m pipeline.cloner <repo_url> <destination>")

    repo_url, destination = sys.argv[1], sys.argv[2]
    path = clone_repository(repo_url, destination)
    print(path)


if __name__ == "__main__":
    main()
