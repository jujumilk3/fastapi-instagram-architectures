def matches_query(name: str, query: str) -> bool:
    return query.lower() in name.lower()
