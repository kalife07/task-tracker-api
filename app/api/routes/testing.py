from fastapi import APIRouter, HTTPException, status

from app import storage
from app.core.config import settings

router = APIRouter()


@router.post(
    "/test/reset",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["testing"],
    include_in_schema=False,
)
def reset_test_storage() -> None:
    """Clear in-memory task storage. Available only when APP_ENV=test.

    Intended for the JS/Jest test suite's ``beforeEach``/``afterEach``
    hooks, which call this between tests to reset state. Hidden from the
    OpenAPI schema (``include_in_schema=False``).

    Returns:
        None: Responds with an empty body and HTTP 204 on success.

    Raises:
        HTTPException: 404 if ``settings.app_env`` is not ``"test"``.

    Example:
        POST /test/reset -> 204 (only when APP_ENV=test, otherwise 404)
    """
    if settings.app_env != "test":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    storage._reset()
