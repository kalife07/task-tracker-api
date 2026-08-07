from pydantic import BaseModel


class VersionResponse(BaseModel):
    """Schema returned by GET /version."""
    version: str
