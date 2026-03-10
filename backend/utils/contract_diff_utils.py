import difflib
from typing import List, Dict, Any


def generate_line_diff(old_text: str, new_text: str) -> List[Dict[str, Any]]:
    """Return a list of (tag, old_line, new_line) tuples representing the line diff."""
    matcher = difflib.SequenceMatcher(None, old_text.splitlines(), new_text.splitlines())
    result: List[Dict[str, Any]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        result.append({
            "tag": tag,
            "old_lines": old_text.splitlines()[i1:i2],
            "new_lines": new_text.splitlines()[j1:j2],
        })
    return result


def format_diff_for_storage(diff: List[Dict[str, Any]]) -> str:
    """Serialise the diff list to a compact string for DB storage."""
    import json
    return json.dumps(diff)


def format_diff_for_display(diff: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return the diff list enriched with color hints for UI rendering."""
    colors = {"equal": "white", "insert": "green", "delete": "red", "replace": "yellow"}
    return [{**entry, "color": colors.get(entry["tag"], "white")} for entry in diff]
