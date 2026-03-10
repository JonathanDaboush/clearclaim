import re


def slugify_project_name(name: str) -> str:
    """Convert a project name to a URL-safe slug (lowercase, hyphens, no special chars)."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug


def is_valid_project_name(name: str) -> bool:
    """Return True if the name is non-empty and at least 3 characters long."""
    return bool(name and len(name.strip()) >= 3)
