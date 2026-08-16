"""OpenRouter (OpenAI-compatible) calls for clustering and extraction — the two calls in
.docs/LLM_PIPELINE.md. Structured output only (JSON schema derived from the Pydantic models in
.types), never free-text parsing, per that doc's hard rule."""

import httpx
from pydantic import BaseModel

from app.config import get_settings

from .types import ClusterOutput, ExtractOutput

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def _generate(prompt: str, schema_name: str, schema: type[BaseModel]) -> str:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
            json={
                "model": settings.openrouter_model,
                "temperature": 0.0,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"name": schema_name, "schema": schema.model_json_schema()},
                },
            },
        )
        res.raise_for_status()
        data = res.json()

    return data["choices"][0]["message"]["content"]


def _format_results(results: list[tuple[str, str, str]]) -> str:
    """results: list of (url, title, snippet)."""
    return "\n\n".join(f"[{i + 1}] {title}\nURL: {url}\n{snippet}" for i, (url, title, snippet) in enumerate(results))


CLUSTER_PROMPT = """You are clustering public web search results into distinct real people who share a name.

Query: name="{name}"{filters}

Search results:
{results}

Group these results into distinct people, not one cluster per result. Two results describing the
same person in different words belong in one cluster; a result describing a clearly different
person (different city, job, age) is a separate cluster.

Hard rules:
- Every cluster must cite at least one source_urls entry drawn verbatim from the URLs above — never invent a cluster with no supporting result.
- If the evidence is too thin to confidently tell two people apart, merge them into one cluster rather than over-splitting. Fewer, more confident clusters beat many low-confidence ones.
- Do not invent details not present in the result titles/snippets above.
- confidence is 0-1: how sure you are this cluster represents one distinct real person (not how famous or important they are).
- photo_url: only set if a result plausibly links to an actual photo of this person; otherwise null.
"""

EXTRACT_PROMPT = """You are extracting a structured profile for one specific person from public web pages, citing a source for every fact.

Candidate: {candidate_label}
{candidate_summary}

Source pages (use ONLY this text — never fill from general knowledge):
{pages}

Hard rule, non-negotiable: no source, no field. If a fact cannot be tied to a specific snippet from
the pages above, leave that field null/empty — never fill it from inference or outside knowledge.
One `sources` entry per fact actually used (a field can cite more than one source); every non-null
field in `fields` must have at least one matching `sources` entry with supports_field equal to
that field's name. `full_name` and `summary` are the only fields allowed to be non-empty without
needing to appear in `sources` themselves, but everything in `summary` must still be grounded in
the pages above.
"""


async def cluster_candidates(
    name: str, filters: dict[str, str | list[str]], results: list[tuple[str, str, str]]
) -> ClusterOutput:
    filters_text = "".join(f", {k}={v}" for k, v in filters.items() if v)
    prompt = CLUSTER_PROMPT.format(name=name, filters=filters_text, results=_format_results(results))

    content = await _generate(prompt, "ClusterOutput", ClusterOutput)
    return ClusterOutput.model_validate_json(content)


async def extract_profile(candidate_label: str, candidate_summary: str, pages: list[tuple[str, str, str]]) -> ExtractOutput:
    """pages: list of (url, title, text)."""
    prompt = EXTRACT_PROMPT.format(
        candidate_label=candidate_label, candidate_summary=candidate_summary, pages=_format_results(pages)
    )

    content = await _generate(prompt, "ExtractOutput", ExtractOutput)
    return ExtractOutput.model_validate_json(content)
