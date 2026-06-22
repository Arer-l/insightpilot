from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def _to_float(value: Any) -> float | Any:
    return float(value) if isinstance(value, Decimal) else value


def _period_filter_sql(city: str | None) -> str:
    city_filter = "AND city = :city" if city else ""
    return f"""
        payment_status = 'paid'
        AND order_date >= :start_date
        AND order_date < :end_date
        {city_filter}
    """


def _get_period_gmv(
    db: Session,
    start_date: str,
    end_date: str,
    city: str | None,
) -> float:
    result = db.execute(
        text(
            f"""
            SELECT COALESCE(ROUND(SUM(order_amount), 2), 0) AS gmv
            FROM ecommerce_orders
            WHERE {_period_filter_sql(city)}
            """
        ),
        {"start_date": start_date, "end_date": end_date, "city": city},
    ).mappings().one()

    return float(result["gmv"])


def _get_dimension_breakdown(
    db: Session,
    dimension: str,
    current_start_date: str,
    current_end_date: str,
    comparison_start_date: str,
    comparison_end_date: str,
    city: str | None,
    total_change: float,
) -> list[dict[str, Any]]:
    if dimension not in {"channel", "category"}:
        raise ValueError(f"Unsupported breakdown dimension: {dimension}")

    city_filter = "AND city = :city" if city else ""
    result = db.execute(
        text(
            f"""
            WITH current_period AS (
                SELECT
                    {dimension} AS dimension_value,
                    COALESCE(SUM(order_amount), 0) AS current_gmv
                FROM ecommerce_orders
                WHERE payment_status = 'paid'
                  AND order_date >= :current_start_date
                  AND order_date < :current_end_date
                  {city_filter}
                GROUP BY {dimension}
            ),
            comparison_period AS (
                SELECT
                    {dimension} AS dimension_value,
                    COALESCE(SUM(order_amount), 0) AS comparison_gmv
                FROM ecommerce_orders
                WHERE payment_status = 'paid'
                  AND order_date >= :comparison_start_date
                  AND order_date < :comparison_end_date
                  {city_filter}
                GROUP BY {dimension}
            )
            SELECT
                COALESCE(c.dimension_value, p.dimension_value) AS dimension_value,
                ROUND(COALESCE(c.current_gmv, 0), 2) AS current_gmv,
                ROUND(COALESCE(p.comparison_gmv, 0), 2) AS comparison_gmv,
                ROUND(COALESCE(c.current_gmv, 0) - COALESCE(p.comparison_gmv, 0), 2)
                    AS change_amount
            FROM current_period c
            FULL OUTER JOIN comparison_period p
                ON c.dimension_value = p.dimension_value
            ORDER BY ABS(COALESCE(c.current_gmv, 0) - COALESCE(p.comparison_gmv, 0)) DESC
            """
        ),
        {
            "current_start_date": current_start_date,
            "current_end_date": current_end_date,
            "comparison_start_date": comparison_start_date,
            "comparison_end_date": comparison_end_date,
            "city": city,
        },
    )

    rows = []
    for row in result.mappings():
        change_amount = _to_float(row["change_amount"])
        contribution_rate = (
            round(change_amount / total_change, 4)
            if total_change not in {0, 0.0}
            else 0
        )
        rows.append(
            {
                dimension: row["dimension_value"],
                "current_gmv": _to_float(row["current_gmv"]),
                "comparison_gmv": _to_float(row["comparison_gmv"]),
                "change_amount": change_amount,
                "contribution_rate": contribution_rate,
            }
        )
    return rows


def _build_summary(
    city: str | None,
    current_days: int,
    change_amount: float,
    change_percentage: float | None,
    by_channel: list[dict[str, Any]],
    by_category: list[dict[str, Any]],
) -> str:
    scope = f"{city} " if city else ""
    direction = "上升" if change_amount > 0 else "下降" if change_amount < 0 else "基本持平"
    percentage_text = (
        f"{abs(change_percentage) * 100:.2f}%"
        if change_percentage is not None
        else "无法计算百分比"
    )

    channel_text = by_channel[0]["channel"] if by_channel else "暂无明显渠道"
    category_text = by_category[0]["category"] if by_category else "暂无明显品类"

    if change_amount == 0:
        return f"{scope}最近{current_days}天 GMV 与对比周期基本持平，暂未发现明显变化来源。"

    return (
        f"{scope}最近{current_days}天 GMV 较对比周期{direction}{percentage_text}，"
        f"变化主要集中在 {channel_text} 渠道和 {category_text} 品类。"
    )


def analyze_gmv_change(
    db: Session,
    current_days: int = 14,
    compare_days: int = 14,
    city: str | None = None,
) -> dict[str, Any]:
    dates = db.execute(
        text(
            """
            SELECT
                CURRENT_DATE::DATE AS current_end_date,
                (CURRENT_DATE - (:current_days || ' days')::INTERVAL)::DATE
                    AS current_start_date,
                (CURRENT_DATE - (:current_days || ' days')::INTERVAL)::DATE
                    AS comparison_end_date,
                (CURRENT_DATE - ((:current_days + :compare_days) || ' days')::INTERVAL)::DATE
                    AS comparison_start_date
            """
        ),
        {"current_days": current_days, "compare_days": compare_days},
    ).mappings().one()

    current_start_date = dates["current_start_date"].isoformat()
    current_end_date = dates["current_end_date"].isoformat()
    comparison_start_date = dates["comparison_start_date"].isoformat()
    comparison_end_date = dates["comparison_end_date"].isoformat()

    current_gmv = _get_period_gmv(db, current_start_date, current_end_date, city)
    comparison_gmv = _get_period_gmv(
        db,
        comparison_start_date,
        comparison_end_date,
        city,
    )

    change_amount = round(current_gmv - comparison_gmv, 2)
    change_percentage = (
        round(change_amount / comparison_gmv, 4) if comparison_gmv else None
    )

    by_channel = _get_dimension_breakdown(
        db,
        "channel",
        current_start_date,
        current_end_date,
        comparison_start_date,
        comparison_end_date,
        city,
        change_amount,
    )
    by_category = _get_dimension_breakdown(
        db,
        "category",
        current_start_date,
        current_end_date,
        comparison_start_date,
        comparison_end_date,
        city,
        change_amount,
    )

    return {
        "metric": "gmv",
        "filters": {
            "city": city,
        },
        "current_period": {
            "days": current_days,
            "start_date": current_start_date,
            "end_date": current_end_date,
            "gmv": current_gmv,
        },
        "comparison_period": {
            "days": compare_days,
            "start_date": comparison_start_date,
            "end_date": comparison_end_date,
            "gmv": comparison_gmv,
        },
        "change": {
            "absolute": change_amount,
            "percentage": change_percentage,
        },
        "breakdowns": {
            "by_channel": by_channel,
            "by_category": by_category,
        },
        "summary": _build_summary(
            city,
            current_days,
            change_amount,
            change_percentage,
            by_channel,
            by_category,
        ),
    }
