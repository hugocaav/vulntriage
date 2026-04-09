from __future__ import annotations

import argparse
import os
import shutil
import stat
from pathlib import Path
from urllib.parse import urlparse

try:
    from git import Repo
    from git.exc import GitCommandError
except ImportError:  # pragma: no cover
    Repo = None

    class GitCommandError(Exception):
        """Fallback exception when GitPython is unavailable."""

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "repos"


def _validate_github_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Invalid URL: only http(s) GitHub repository URLs are supported.")

    hostname = (parsed.netloc or "").lower()
    if hostname not in {"github.com", "www.github.com"}:
        raise ValueError("Invalid URL: only public GitHub repositories are supported.")

    path_parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(path_parts) != 2:
        raise ValueError("Invalid URL: expected https://github.com/<owner>/<repo>.")

    owner, repo_name = path_parts
    repo_name = repo_name.removesuffix(".git")
    if not owner or not repo_name:
        raise ValueError("Invalid URL: repository owner and name are required.")

    return owner, repo_name


def _build_clone_path(owner: str, repo_name: str) -> Path:
    return (BASE_OUTPUT_DIR / f"{owner}__{repo_name}").resolve()


def _on_remove_error(func: object, path: str, exc_info: tuple[object, object, object]) -> None:
    del exc_info
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_existing_clone(target_path: Path) -> None:
    if target_path.exists():
        shutil.rmtree(target_path, onerror=_on_remove_error)


def clone_repo(repo_url: str) -> str:
    """Clone a public GitHub repository into outputs/repos and return its absolute path."""
    if Repo is None:
        raise RuntimeError("GitPython is required. Install it with `pip install gitpython`.")

    owner, repo_name = _validate_github_url(repo_url)
    target_path = _build_clone_path(owner, repo_name)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    _remove_existing_clone(target_path)

    try:
        Repo.clone_from(repo_url, target_path, depth=1, single_branch=True)
    except GitCommandError as exc:
        error_text = (str(exc) or "").lower()
        if "not found" in error_text or "repository not found" in error_text:
            raise FileNotFoundError(f"Repository not found: {repo_url}") from exc
        if "could not resolve host" in error_text or "failed to connect" in error_text:
            raise ConnectionError(f"Network error while cloning repository: {repo_url}") from exc
        if "authentication failed" in error_text or "permission denied" in error_text:
            raise PermissionError(
                f"Repository is not publicly accessible: {repo_url}"
            ) from exc
        raise RuntimeError(f"Failed to clone repository: {repo_url}") from exc

    return str(target_path)


def clone_repository(repo_url: str, destination: str | Path | None = None) -> Path:
    """Backward-compatible wrapper around clone_repo.

    The destination argument is ignored so all clones stay under outputs/repos.
    """
    return Path(clone_repo(repo_url))


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone a public GitHub repository.")
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository URL, for example https://github.com/we45/Vulnerable-Flask-App",
    )
    args = parser.parse_args()

    try:
        print(clone_repo(args.repo))
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
