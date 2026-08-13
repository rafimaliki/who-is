"""The in-memory store (app/shared/store.py) is a module-level singleton shared by the search and
profile domains — reset it between tests so one test's searches/profiles can't leak into
another's."""

import pytest

from app.shared.store import store


@pytest.fixture(autouse=True)
def _reset_store() -> None:
    store.searches.clear()
    store.profiles.clear()
