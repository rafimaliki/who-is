"""Collapse the stub's demo-pacing delays for tests — those exist for a human watching the UI,
not for a test suite."""

import pytest

from app import stub


@pytest.fixture(autouse=True)
def _no_stub_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stub, "SEARCH_DELAY_S", 0)
    monkeypatch.setattr(stub, "SELECT_DELAY_S", 0)
