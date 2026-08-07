from datetime import date, datetime, timezone
from typing import Optional

MAX_TAGS_PER_TASK = 10
MAX_TAG_LENGTH = 30


def parse_due_date_to_date(due_date: str) -> date:
    """Parse an ISO-8601 date or timestamp string into a date.

    Args:
        due_date (str): A date string. Treated as ``YYYY-MM-DD`` when
            exactly 10 characters long; otherwise parsed as a full
            ISO-8601 timestamp (a trailing ``Z`` is treated as ``+00:00``).

    Returns:
        date: The parsed calendar date (time-of-day is discarded for
        timestamp inputs).

    Raises:
        ValueError: If ``due_date`` is not a valid ISO-8601 date or
            timestamp string.
    """
    if len(due_date) == 10:
        return date.fromisoformat(due_date)
    parsed = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
    return parsed.date()


def validate_due_date(value: Optional[str]) -> Optional[str]:
    """Validate and normalize an optional due_date payload value.

    Args:
        value (Optional[str]): The raw due_date input. ``None`` or a
            blank/whitespace-only string is treated as "no due date".

    Returns:
        Optional[str]: ``None`` if ``value`` was empty/blank; otherwise
        the input with leading/trailing whitespace stripped (the
        original string format is preserved, not reformatted to a
        canonical date).

    Raises:
        ValueError: If the stripped value is not a valid ISO-8601 date
            or timestamp string (see ``parse_due_date_to_date``).
    """
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
    """Normalize tag lists: trim, drop empties, and enforce limits.

    Args:
        value (Optional[list[str]]): The raw tag list. ``None`` is
            treated as an empty list.

    Returns:
        list[str]: Tags with whitespace stripped and empty/blank entries
        removed. Order and duplicates are otherwise preserved as given.

    Raises:
        ValueError: If more than ``MAX_TAGS_PER_TASK`` (10) tags remain
            after cleaning, or if any individual tag exceeds
            ``MAX_TAG_LENGTH`` (30) characters.
    """
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
    """Return True when due_date is before today and status is not Done.

    Args:
        due_date (Optional[str]): The task's due_date, expected to
            already be a valid ISO-8601 date/timestamp string (e.g. as
            validated by ``validate_due_date``). ``None`` means no due
            date is set.
        status_value (str): The task's status value (e.g. ``"Done"``).

    Returns:
        bool: False if ``due_date`` is ``None`` or ``status_value`` is
        ``"Done"``. Otherwise True if the parsed due date is strictly
        before today's UTC date.
    """
    if due_date is None or status_value == "Done":
        return False

    today = datetime.now(timezone.utc).date()
    return parse_due_date_to_date(due_date) < today
