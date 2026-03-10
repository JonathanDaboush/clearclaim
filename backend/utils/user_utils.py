import re


def normalize_email(email: str) -> str:
    """Return the email address lowercased and stripped of whitespace."""
    return email.strip().lower()


def is_valid_email(email: str) -> bool:
    """Return True if the email matches a standard address format."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None
