"""Text formatting helpers."""


def normalize_whitespace(value: str) -> str:
    """Collapse repeated whitespace into single spaces."""

    return " ".join(value.split())


def truncate_text(value: str, max_chars: int) -> str:
    """Truncate text to a maximum number of characters."""

    cleaned = normalize_whitespace(value)
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[: max_chars - 3].rstrip()}..."


def clean_lines(lines: list[str]) -> list[str]:
    """Clean markdown-style bullet lines."""

    cleaned: list[str] = []
    for line in lines:
        item = line.strip().lstrip("-*0123456789. ").strip()
        if item:
            cleaned.append(item)
    return cleaned
