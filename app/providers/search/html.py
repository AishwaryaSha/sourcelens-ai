"""Tiny HTML text helpers for search providers."""


def strip_html_tags(value: str) -> str:
    """Remove simple HTML tags from provider snippets."""

    output: list[str] = []
    inside_tag = False
    for char in value:
        if char == "<":
            inside_tag = True
            continue
        if char == ">":
            inside_tag = False
            continue
        if not inside_tag:
            output.append(char)
    return "".join(output).strip()
