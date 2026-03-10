def summarize_contract(content: str) -> str:
    """Return the first 200 characters of contract content as a preview summary."""
    return content[:200].strip() + ("..." if len(content) > 200 else "")


def is_valid_contract_content(content: str) -> bool:
    """Return True if content is non-empty after stripping whitespace."""
    return bool(content and content.strip())
