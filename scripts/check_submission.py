#!/usr/bin/env python3
"""Fast, dependency-free CivicPulse delivery checklist.

Run from the repository root. Normal mode reports gaps without failing so it
can be used during implementation; ``--strict`` exits non-zero for missing
required final-delivery artefacts and is used by the manual audit workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ".env.example",
    ".gitignore",
    ".dockerignore",
    "README.md",
    "compose.yaml",
    "compose.prod.yaml",
    "backend/Dockerfile",
    "frontend/Dockerfile",
    "frontend/nginx/default.conf.template",
    "backend/alembic.ini",
    "backend/openapi.json",
    "backend/scripts/seed.py",
    ".github/workflows/ci.yml",
    "docs/AI-USAGE.md",
    "docs/PROJECT-PLAN.md",
    "docs/PROJECT-CHARTER.md",
    "docs/CONTAINERS.md",
    "docs/ENGINEERING-NOTES.md",
    "docs/RUNBOOK.md",
    "docs/adr/001-triage-provider-boundary.md",
    "docs/adr/002-api-contract.md",
    "docs/adr/003-container-networking.md",
    "docs/adr/004-kubernetes-delivery.md",
    "k8s/base/kustomization.yaml",
    "k8s/overlays/local/kustomization.yaml",
    "scripts/load_test.py",
)

REQUIRED_MARKERS = {
    "README.md": ("Docker", "Kubernetes", "OpenRouter"),
    "docs/AI-USAGE.md": ("Codex", "Human responsibility"),
    "compose.yaml": ("postgres", "redis", "frontend", "backend"),
    ".github/workflows/ci.yml": ("pytest", "npm run test", "trivy"),
}


def check_file(path: str) -> str | None:
    absolute = ROOT / path
    if not absolute.is_file():
        return f"missing file: {path}"
    return None


def check_markers(path: str, markers: tuple[str, ...]) -> list[str]:
    content = (ROOT / path).read_text(encoding="utf-8")
    return [f"{path}: missing marker {marker!r}" for marker in markers if marker not in content]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="return non-zero when a requirement is absent")
    args = parser.parse_args()

    findings = [finding for path in REQUIRED_FILES if (finding := check_file(path))]
    for path, markers in REQUIRED_MARKERS.items():
        if (ROOT / path).is_file():
            findings.extend(check_markers(path, markers))

    if findings:
        print("Delivery gaps:")
        for finding in findings:
            print(f"- {finding}")
        if args.strict:
            return 1
        print("\nNon-strict mode: gaps are expected until Day 3. Re-run with --strict before submission.")
        return 0

    print("Submission checklist passed: required files and basic content markers are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
