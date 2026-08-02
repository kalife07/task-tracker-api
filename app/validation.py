from datetime import date, datetime, timezone
from typing import Optional

MAX_TAGS_PER_TASK = 10
MAX_TAG_LENGTH = 30


def parse_due_date_to_date(due_date: str) -> date:
    """Parse an ISO-8601 date or timestamp string into a date."""
    if len(due_date) == 10:
        return date.fromisoformat(due_date)
    parsed = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
    return parsed.date()


def validate_due_date(value: Optional[str]) -> Optional[str]:
    """Validate and normalize an optional due_date payload value."""
    if value is None or value == "":
        return None

    stripped = value.strip()
    if not stripped:
        return None

    try:
        parse_due_date_to_date(stripped)
    except ValueError as exc:
        raise ValueError("due_date must be a valid ISO-8601 date string") from exc

    return stripped


def validate_tags(value: Optional[list[str]]) -> list[str]:
    """Normalize tag lists: trim, drop empties, and enforce limits."""
    if value is None:
        return []

    cleaned = [tag.strip() for tag in value if tag and tag.strip()]

    if len(cleaned) > MAX_TAGS_PER_TASK:
        raise ValueError(f"tags must contain at most {MAX_TAGS_PER_TASK} items")

    for tag in cleaned:
        if len(tag) > MAX_TAG_LENGTH:
            raise ValueError(
                f"each tag must be at most {MAX_TAG_LENGTH} characters"
            )

    return cleaned


def is_task_overdue(due_date: Optional[str], status_value: str) -> bool:
    """Return True when due_date is before today and status is not Done."""
    if due_date is None or status_value == "Done":
        return False

    today = datetime.now(timezone.utc).date()
    return parse_due_date_to_date(due_date) < today
