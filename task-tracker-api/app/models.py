from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.validation import is_task_overdue, validate_due_date, validate_tags


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Strip whitespace and reject blank or overlong titles.

        Args:
            v (str): The raw title value.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is empty, or longer than
                200 characters.
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        if len(stripped) > 200:
            raise ValueError("title must be at most 200 characters")
        return stripped

    @field_validator("due_date")
    @classmethod
    def validate_due_date_field(cls, v: Optional[str]) -> Optional[str]:
        """Delegate due_date validation to ``app.validation.validate_due_date``.

        Args:
            v (Optional[str]): The raw due_date value.

        Returns:
            Optional[str]: The normalized due_date (see
            ``validate_due_date``).

        Raises:
            ValueError: If ``v`` is not a valid ISO-8601 date/timestamp.
        """
        return validate_due_date(v)

    @field_validator("tags")
    @classmethod
    def validate_tags_field(cls, v: list[str]) -> list[str]:
        """Delegate tag validation to ``app.validation.validate_tags``.

        Args:
            v (list[str]): The raw tags list.

        Returns:
            list[str]: The normalized tags (see ``validate_tags``).

        Raises:
            ValueError: If there are too many tags, or any tag is too
                long.
        """
        return validate_tags(v)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace and reject blank or overlong titles, if set.

        Args:
            v (Optional[str]): The raw title value, or ``None`` if title
                is not being updated.

        Returns:
            Optional[str]: ``None`` unchanged, otherwise the stripped
            title.

        Raises:
            ValueError: If ``v`` is not ``None`` and the stripped title
                is empty, or longer than 200 characters.
        """
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        if len(stripped) > 200:
            raise ValueError("title must be at most 200 characters")
        return stripped

    @field_validator("due_date")
    @classmethod
    def validate_due_date_field(cls, v: Optional[str]) -> Optional[str]:
        """Delegate due_date validation to ``app.validation.validate_due_date``.

        Args:
            v (Optional[str]): The raw due_date value, or ``None`` if
                due_date is not being updated.

        Returns:
            Optional[str]: The normalized due_date (see
            ``validate_due_date``).

        Raises:
            ValueError: If ``v`` is not a valid ISO-8601 date/timestamp.
        """
        return validate_due_date(v)

    @field_validator("tags")
    @classmethod
    def validate_tags_field(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Delegate tag validation to ``app.validation.validate_tags``, if set.

        Args:
            v (Optional[list[str]]): The raw tags list, or ``None`` if
                tags are not being updated.

        Returns:
            Optional[list[str]]: ``None`` unchanged, otherwise the
            normalized tags (see ``validate_tags``).

        Raises:
            ValueError: If there are too many tags, or any tag is too
                long.
        """
        if v is None:
            return v
        return validate_tags(v)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        """Whether this task is overdue.

        Derived at read time from ``due_date`` and ``status`` via
        ``app.validation.is_task_overdue`` — not stored, so it always
        reflects the current date rather than a value computed at write
        time.

        Returns:
            bool: True if ``due_date`` is before today (UTC) and
            ``status`` is not ``Done``; otherwise False.
        """
        return is_task_overdue(self.due_date, self.status.value)
