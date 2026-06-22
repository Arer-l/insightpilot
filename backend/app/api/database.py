from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.tools.sql_tools import get_database_schema

router = APIRouter(prefix="/api/database", tags=["database"])


@router.get("/schema")
def database_schema(
    table_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return get_database_schema(db, table_name=table_name)
