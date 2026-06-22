from typing import Any

from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=50, ge=1, le=200)


class AgentQueryResponse(BaseModel):
    query: str
    intent: str
    tool_name: str
    parameters: dict[str, Any]
    sql: str | None = None
    result: dict[str, Any] | list[dict[str, Any]]
    answer: str
    reasoning_steps: list[str]
