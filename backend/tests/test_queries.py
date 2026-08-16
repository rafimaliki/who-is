"""Unit tests for app/search/queries.py — the ranking rules that decide which search results are
about the person asked for. Pure functions, no network, so these are the cheap place to pin down
the behavior that used to let famous namesakes through."""

from app.search import queries

NAME = "Ahmad Rafi Maliki"


def test_handles_puts_the_surname_tail_first() -> None:
    """Handle continuity: people reuse one handle, and it's usually the distinctive tail of their
    name, not the given name every second person shares."""
    assert queries.handles(NAME)[0] == "rafimaliki"
    assert "ahmadrafimaliki" in queries.handles(NAME)
    assert "ahmad-rafi-maliki" in queries.handles(NAME)


def test_handles_deduplicates() -> None:
    # For a two-token name, "tokens[1:]" and "last two tokens" collide.
    assert len(queries.handles("Rafi Maliki")) == len(set(queries.handles("Rafi Maliki")))


def test_build_quotes_the_name_for_exact_phrase_matching() -> None:
    built = queries.build(NAME, {})
    assert built[0] == '"Ahmad Rafi Maliki"'
    assert any("site:linkedin.com" in q for q in built)
    assert "rafimaliki" in built


def test_build_appends_filters_to_the_broad_query_only() -> None:
    built = queries.build(NAME, {"country": "Indonesia", "occupation": "engineer"})
    assert built[0] == '"Ahmad Rafi Maliki" Indonesia engineer'
    # The site: query stays unconstrained - extra terms there just return nothing.
    assert not any("Indonesia" in q for q in built[1:])


def test_a_result_missing_a_name_token_scores_zero() -> None:
    """The exact bug this was written for: "Ahmad Dhani" outranked the actual person because it
    matched on the given name alone."""
    assert queries.score(NAME, "Ahmad Dhani - Wikipedia", "https://id.wikipedia.org/wiki/Ahmad_Dhani", "musician") == 0
    assert queries.score(NAME, "Ahmad - Wikipedia", "https://en.wikipedia.org/wiki/Ahmad", "a given name") == 0


def test_a_full_name_match_on_a_personal_site_outscores_a_passing_mention() -> None:
    own_site = queries.score(NAME, "Ahmad Rafi Maliki", "https://www.rafimaliki.xyz/", "portfolio")
    mention = queries.score(NAME, "Alumni list", "https://example.com/alumni", "... Ahmad Rafi Maliki ...")
    assert own_site > mention > 0


def test_name_directory_pages_are_pushed_down() -> None:
    """"300+ Ahmad Rafi profiles" carries the name but describes no single person."""
    directory = queries.score(NAME, '300+ "Ahmad Rafi Maliki" profiles', "https://www.linkedin.com/pub/dir/Ahmad+Rafi/Maliki", "")
    real = queries.score(NAME, "Ahmad Rafi Maliki", "https://www.linkedin.com/in/ahmad-rafi-maliki", "")
    assert real > directory


def test_rank_drops_namesakes_and_orders_by_score() -> None:
    results = [
        ("https://en.wikipedia.org/wiki/Ahmad", "Ahmad - Wikipedia", "a given name"),
        ("https://id.wikipedia.org/wiki/Ahmad_Dhani", "Ahmad Dhani", "Indonesian musician"),
        ("https://www.rafimaliki.xyz/", "Ahmad Rafi Maliki", "portfolio"),
        ("https://github.com/rafimaliki", "Ahmad Rafi Maliki rafimaliki", "profile"),
    ]
    ranked = queries.rank(NAME, results, limit=10)

    # Both full-name pages survive; both single-token namesakes are gone. Their relative order is
    # not pinned - either is a correct first result.
    assert set(url for url, _, _ in ranked) == {"https://www.rafimaliki.xyz/", "https://github.com/rafimaliki"}


def test_rank_falls_back_to_the_unfiltered_head_when_nothing_scores() -> None:
    """A hard filter that silently yields no candidates is worse than a noisy one — the LLM
    clustering step is the second line of defence."""
    results = [("https://example.com/a", "Unrelated", ""), ("https://example.com/b", "Also unrelated", "")]
    assert queries.rank(NAME, results, limit=1) == results[:1]
