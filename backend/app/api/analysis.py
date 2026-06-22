from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analysis_service import analyze_gmv_change

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/gmv-change")
def gmv_change(
    current_days: int = Query(default=14, ge=1, le=90),
    compare_days: int = Query(default=14, ge=1, le=90),
    city: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return analyze_gmv_change(
        db,
        current_days=current_days,
        compare_days=compare_days,
        city=city,
    )
