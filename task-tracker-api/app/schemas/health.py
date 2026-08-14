# health.py - Pydantic response model for the /health endpoint.
# Defining response shapes as Pydantic models gives you automatic
# validation, serialization, and OpenAPI schema generation for free.

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema returned by GET /health."""

    status: str
    timestamp: str
