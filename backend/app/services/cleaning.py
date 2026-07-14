"""
Cleans raw LinkedIn paste/export text before it goes to the LLM.

LinkedIn profile pages (and copy-pastes of them) are full of repeated nav
chrome, "· 3rd+", follower counts, ads, and "See more" boilerplate. Stripping
this before extraction meaningfully improves extraction quality and cuts
token cost.
"""
import re

_NAV_PATTERNS = [
    r"^Skip to (main )?content$",
    r"^Home$",
    r"^My Network$",
    r"^Jobs$",
    r"^Messaging$",
    r"^Notifications$",
    r"^Sign in$",
    r"^Join now$",
    r"^See more$",
    r"^See less$",
    r"^\d+(st|nd|rd|th)\+? degree connection$",
    r"^\d+ mutual connections?$",
    r"^Follow$",
    r"^Connect$",
    r"^Message$",
    r"^More$",
    r"^Promoted$",
    r"^Ad\b.*$",
    r"^\d+[,.]?\d* followers?$",
    r"^Report this (profile|post)$",
    r"^Show all \d+ .*$",
    r"^Contact info$",
    r"^\d+ comments?$",
    r"^\d+ shares?$",
    r"^Like\s*Comment\s*Share$",
]

_COMPILED_NAV = [re.compile(p, re.IGNORECASE) for p in _NAV_PATTERNS]


def clean_profile_text(raw_text: str) -> str:
    """Remove navigation chrome, dedupe blank lines/whitespace, and trim."""
    if not raw_text:
        return ""

    lines = raw_text.splitlines()
    cleaned_lines: list[str] = []
    seen_recent: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(pattern.match(stripped) for pattern in _COMPILED_NAV):
            continue
        # Drop immediate duplicate lines (common in copy-pasted DOM text)
        if seen_recent and stripped == seen_recent[-1]:
            continue
        cleaned_lines.append(stripped)
        seen_recent.append(stripped)
        if len(seen_recent) > 3:
            seen_recent.pop(0)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
