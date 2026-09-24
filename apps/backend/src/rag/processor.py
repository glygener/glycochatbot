import re


class QueryProcessor:
    """Normalize and clean user questions before retrieval."""

    def process(self, query: str) -> str:
        query = query.strip()
        query = re.sub(r"\s+", " ", query)
        return query
