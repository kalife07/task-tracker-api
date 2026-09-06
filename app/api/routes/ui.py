# ui.py - Serves the Kanban board frontend from the API itself, so
# http://localhost:8000 opens the working UI rather than a bare 404.
#
# frontend/index.html is a single self-contained file (inline CSS and JS,
# no external assets), so one file route is all it needs — there is no
# static asset directory to mount.

from pathlib import Path

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import FileResponse

router = APIRouter()

# <project root>/frontend/index.html — this file is app/api/routes/ui.py,
# so three parents up from the app package is the project root.
FRONTEND_INDEX = Path(__file__).resolve().parents[3] / "frontend" / "index.html"


@router.get(
    "/",
    include_in_schema=False,
    response_class=FileResponse,
)
def serve_board() -> FileResponse:
    """Serve the Kanban board UI at the site root.

    Returns:
        FileResponse: ``frontend/index.html``, sent with
        ``Cache-Control: no-cache`` so an edited board shows up on
        reload instead of being served from the browser cache.

    Raises:
        HTTPException: 404 if ``frontend/index.html`` is missing — for
            example in a container image built without the frontend
            directory. The API routes keep working in that case.
    """
    if not FRONTEND_INDEX.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Frontend not found at {FRONTEND_INDEX}. The API is running; "
                "see /docs for the endpoints."
            ),
        )

    return FileResponse(
        FRONTEND_INDEX,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Answer the browser's automatic favicon request.

    Returns:
        Response: An empty 204, so loading the board does not log a
        confusing 404 for an icon the app does not ship.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
