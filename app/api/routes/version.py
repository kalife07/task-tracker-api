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
    """Return the running API's version string.

    Returns:
        VersionResponse: ``version`` set to the ``app.__version__`` constant.

    Example:
        GET /version -> 200 {"version": "0.1.0"}
    """
    return VersionResponse(version=__version__)
