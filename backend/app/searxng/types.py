from dataclasses import dataclass


@dataclass
class SearxResult:
    title: str
    url: str
    content: str
