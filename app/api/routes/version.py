from fastapi import APIRouter

from app import __version__
from app.schemas.version import VersionResponse

router = APIRouter()


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Get API version",
    description="Returns the current API version.",
)
def get_version() -> VersionResponse:
    """Return the API's version string."""
    return VersionResponse(version=__version__)
