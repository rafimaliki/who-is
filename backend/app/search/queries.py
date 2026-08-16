"""Query expansion and result scoring for person search — the OSINT bits that decide *what* to ask
a search provider and *which* answers are actually about the person asked for.

Pure functions, no I/O, so the ranking rules can be tested without touching a search provider.

Two standard OSINT techniques are what make this work on a low-profile person:
- exact-phrase search, so "Ahmad Rafi Maliki" can't match a page that only says "Ahmad"
- handle continuity — people reuse one handle across their site/GitHub/Instagram, and that handle
  is usually derivable from their name, so it's worth searching for directly
"""

import re

# Platforms worth a site: query of their own — the ones that host a person's profile page and let
# search engines index it.
SOCIAL_SITES = ["linkedin.com", "instagram.com", "x.com", "twitter.com", "facebook.com", "tiktok.com", "youtube.com", "github.com"]

# Hosts worth a small ranking bump: a hit here is a person's own page far more often than a hit on
# a random content site is. The social platforms plus the places people publish under their name.
IDENTITY_HOSTS = (*SOCIAL_SITES, "medium.com", "about.me", "scholar.google.com", "researchgate.net", "orcid.org")

# Directory/aggregator pages that match a name but describe no single person ("300+ Ahmad Rafi
# profiles"). They rank well and are pure noise for clustering.
DIRECTORY_URL_MARKERS = ("/pub/dir/", "/directory/", "idcrawl.com", "peekyou.com", "spokeo.com", "zoominfo.com")


def name_tokens(name: str) -> list[str]:
    """Lowercased alphabetic tokens of a name, in order. Non-ascii scripts fall through to a
    whitespace split so a fully non-latin name still yields something to match on."""
    tokens = [t for t in re.findall(r"[^\W\d_]+", name.lower(), flags=re.UNICODE) if len(t) >= 2]
    return tokens


def handles(name: str) -> list[str]:
    """Likely usernames for a person, most-distinctive first.

    "Ahmad Rafi Maliki" -> rafimaliki, ahmadrafimaliki, ahmad-rafi-maliki, arafimaliki.
    Dropping the given name first is deliberate: it's the least distinctive token (every second
    Ahmad shares it), and "surname-ish tail only" is the most common real-world handle shape.
    """
    tokens = name_tokens(name)
    if not tokens:
        return []
    if len(tokens) == 1:
        return tokens

    candidates = [
        "".join(tokens[1:]),  # rafimaliki
        "".join(tokens),  # ahmadrafimaliki
        "-".join(tokens),  # ahmad-rafi-maliki
        tokens[0][0] + "".join(tokens[1:]),  # arafimaliki
        "".join(tokens[-2:]),  # last two, same as [1:] for a 3-token name
    ]
    seen: set[str] = set()
    return [h for h in candidates if len(h) >= 4 and not (h in seen or seen.add(h))]


def build(name: str, filters: dict[str, object]) -> list[str]:
    """The query set for one search, most-valuable first.

    Deliberately small — against a metered provider every entry here is a billed request, and the
    exact-phrase query alone does most of the work. Extra filter terms go on the broad query only;
    adding them to the site:/handle queries just over-constrains them into returning nothing.
    """
    quoted = f'"{name}"'

    extras = [str(filters[k]) for k in ("country", "occupation", "employer") if filters.get(k)]
    aliases = filters.get("aliases")
    if aliases:
        extras.extend(str(a) for a in aliases)  # type: ignore[union-attr]

    broad = " ".join([quoted, *extras])
    social = f"{quoted} (" + " OR ".join(f"site:{s}" for s in SOCIAL_SITES) + ")"

    queries = [broad, social]
    queries.extend(handles(name)[:2])
    # Dedupe while preserving order — a single-token name makes broad and handle queries collide.
    seen: set[str] = set()
    return [q for q in queries if not (q in seen or seen.add(q))]


def score(name: str, result_title: str, result_url: str, result_snippet: str) -> int:
    """How likely this result is about the person named, not someone who merely shares a token.

    Coverage of the *full* name is what matters — a page carrying every token of "Ahmad Rafi
    Maliki" is about him; a page carrying only "Ahmad" is about one of millions of other people.
    """
    tokens = name_tokens(name)
    if not tokens:
        return 0

    title, url, snippet = result_title.lower(), result_url.lower(), result_snippet.lower()
    haystack = f"{title} {url} {snippet}"

    covered = sum(1 for t in tokens if t in haystack)
    if covered < len(tokens):
        # Missing a name token is disqualifying, not just a penalty. Callers keep a fallback path
        # for the case where this filters everything out.
        return 0

    points = 10
    points += 5 * sum(1 for t in tokens if t in title)
    points += 3 * sum(1 for t in tokens if t in url)

    if any(h in url for h in handles(name)):
        points += 8
    if any(host in url for host in IDENTITY_HOSTS):
        points += 4
    if any(marker in url for marker in DIRECTORY_URL_MARKERS):
        points -= 15  # matches the name but describes no one person

    return max(points, 0)


def rank(name: str, results: list[tuple[str, str, str]], limit: int) -> list[tuple[str, str, str]]:
    """Sorts (url, title, snippet) results by `score`, drops the zero-scored, caps at `limit`.

    Returns the unranked head instead of an empty list when nothing scores — a hard filter that
    silently produces no candidates is worse than a noisy one, and the LLM clustering step is the
    second line of defence.
    """
    scored = [(score(name, title, url, snippet), (url, title, snippet)) for url, title, snippet in results]
    keepers = sorted([s for s in scored if s[0] > 0], key=lambda s: s[0], reverse=True)
    if not keepers:
        return results[:limit]
    return [r for _, r in keepers[:limit]]
