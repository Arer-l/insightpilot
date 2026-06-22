from typing import Any

from pydantic import BaseModel, Field


class SqlQueryRequest(BaseModel):
    sql: str = Field(..., min_length=1)
    limit: int = Field(default=50, ge=1, le=200)


class SqlValidationResult(BaseModel):
    is_valid: bool
    reason: str | None = None


class SqlQueryResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    validation: SqlValidationResult
