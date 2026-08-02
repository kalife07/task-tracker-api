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
    """Clear in-memory task storage. Available only when APP_ENV=test."""
    if settings.app_env != "test":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    storage._reset()
