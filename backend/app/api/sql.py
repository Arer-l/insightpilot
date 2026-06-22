from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sql import SqlQueryRequest, SqlQueryResponse
from app.tools.sql_tools import execute_readonly_sql

router = APIRouter(prefix="/api/sql", tags=["sql"])


@router.post("/execute", response_model=SqlQueryResponse)
def execute_sql(
    request: SqlQueryRequest,
    db: Session = Depends(get_db),
) -> dict:
    return execute_readonly_sql(db, request.sql, limit=request.limit)
