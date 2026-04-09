from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from pipeline import cloner


def test_clone_repo_rejects_non_github_url():
    with pytest.raises(ValueError, match="public GitHub repositories"):
        cloner.clone_repo("https://gitlab.com/example/project")


def test_clone_repo_reclones_into_outputs(monkeypatch):
    cloned_targets: list[Path] = []

    class FakeRepo:
        @staticmethod
        def clone_from(repo_url: str, destination: Path, depth: int, single_branch: bool) -> None:
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "README.md").write_text(repo_url, encoding="utf-8")
            cloned_targets.append(destination)

    monkeypatch.setattr(cloner, "Repo", FakeRepo)
    target = Path(cloner.clone_repo("https://github.com/example/project"))

    assert target.is_absolute()
    assert target == cloner.BASE_OUTPUT_DIR.resolve() / "example__project"
    assert (target / "README.md").exists()
    assert cloned_targets == [target]

    shutil.rmtree(target)


def test_clone_repo_replaces_existing_clone(monkeypatch):
    class FakeRepo:
        @staticmethod
        def clone_from(repo_url: str, destination: Path, depth: int, single_branch: bool) -> None:
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "fresh.txt").write_text(repo_url, encoding="utf-8")

    monkeypatch.setattr(cloner, "Repo", FakeRepo)
    target = cloner.BASE_OUTPUT_DIR.resolve() / "example__fresh"
    target.mkdir(parents=True, exist_ok=True)
    (target / "stale.txt").write_text("old", encoding="utf-8")

    result = Path(cloner.clone_repo("https://github.com/example/fresh"))

    assert result == target
    assert not (target / "stale.txt").exists()
    assert (target / "fresh.txt").exists()

    shutil.rmtree(target)
