"""In-memory persistence shared by the search and profile domains — search writes both dicts
(candidates when a search runs, a profile when a candidate is selected), profile only reads
`profiles`. Matches the stub this replaced; see .docs/DATA_MODEL.md for the SQLite tables this
becomes once the POC needs runs to survive a restart."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.profile.types import ProfileResponse
    from app.search.types import Candidate


@dataclass
class StoredCandidate:
    candidate: "Candidate"
    label: str
    summary: str
    # URLs that grounded this cluster during search — a fallback data source for the deep dive if
    # a fresh scoped search comes up completely empty (e.g. every SearXNG engine rate-limited).
    source_urls: list[str]


@dataclass
class Store:
    searches: dict[str, list[StoredCandidate]] = field(default_factory=dict)
    profiles: dict[str, "ProfileResponse"] = field(default_factory=dict)


store = Store()
