from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.order_service import (
    get_order_metrics,
    get_order_summary_by_category,
    get_order_summary_by_channel,
    get_order_summary_by_city,
    get_recent_orders,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("/summary")
def order_summary(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return get_order_summary_by_city(db)


@router.get("/metrics")
def order_metrics(db: Session = Depends(get_db)) -> dict[str, Any]:
    return get_order_metrics(db)


@router.get("/by-channel")
def order_summary_by_channel(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return get_order_summary_by_channel(db)


@router.get("/by-category")
def order_summary_by_category(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return get_order_summary_by_category(db)


@router.get("/recent")
def recent_orders(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return get_recent_orders(db, limit=limit)
