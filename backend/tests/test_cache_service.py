"""Tests for the TriageCache service."""

from __future__ import annotations

import pytest

from app.services.cache import TriageCache


def test_different_texts_produce_different_keys() -> None:
    k1 = TriageCache.key_for("burst water pipe", "Street 1", "rules:v1")
    k2 = TriageCache.key_for("broken street light", "Street 2", "rules:v1")
    assert k1 != k2


def test_same_inputs_produce_same_key() -> None:
    k1 = TriageCache.key_for("burst water pipe", "Street 1", "rules:v1")
    k2 = TriageCache.key_for("burst water pipe", "Street 1", "rules:v1")
    assert k1 == k2


def test_key_normalises_case() -> None:
    k1 = TriageCache.key_for("Burst Water Pipe", "Street 1", "rules:v1")
    k2 = TriageCache.key_for("burst water pipe", "street 1", "rules:v1")
    assert k1 == k2


def test_different_providers_produce_different_keys() -> None:
    k1 = TriageCache.key_for("same text", "same location", "rules:v1")
    k2 = TriageCache.key_for("same text", "same location", "llm:gpt-4o")
    assert k1 != k2
