from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
from app.services.agent_service import run_agent_query

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/query", response_model=AgentQueryResponse)
def agent_query(
    request: AgentQueryRequest,
    db: Session = Depends(get_db),
) -> dict:
    return run_agent_query(db, request.query, limit=request.limit)
