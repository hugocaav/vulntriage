# vulntriage

AI-powered vulnerability triage pipeline for open-source repositories. It combines static analysis with LLM reasoning to reduce false positives and prioritize real-world exploitability.

## Structure

- `pipeline/`: clone, scanning, LLM triage, and report generation.
- `api/`: FastAPI service to trigger analyses and fetch reports.
- `dashboard/`: Next.js frontend placeholder for visualization and control.
- `k8s/`: deployment templates for running analyses as Kubernetes Jobs.
- `tests/`: initial unit tests for scanner and triage modules.

## Quick start

1. Copy `.env.example` to `.env`.
2. Build local services with `docker compose up --build`.
3. Run tests with `pytest`.

## Notes

- `dashboard/` is intentionally scaffold-only for now.
- `api/routes` was initialized as a Python package to keep imports clean.
- Secrets should live in runtime environment configuration, never in Git.
