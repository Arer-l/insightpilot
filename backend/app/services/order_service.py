from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def _to_float(value: Any) -> float | Any:
    return float(value) if isinstance(value, Decimal) else value


def get_order_summary_by_city(db: Session) -> list[dict[str, Any]]:
    result = db.execute(
        text(
            """
            SELECT
                city,
                COUNT(*) AS orders,
                ROUND(SUM(order_amount), 2) AS gmv
            FROM ecommerce_orders
            WHERE payment_status = 'paid'
            GROUP BY city
            ORDER BY gmv DESC
            """
        )
    )

    rows = []
    for row in result.mappings():
        rows.append(
            {
                "city": row["city"],
                "orders": row["orders"],
                "gmv": _to_float(row["gmv"]),
            }
        )
    return rows


def get_order_metrics(db: Session) -> dict[str, Any]:
    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) AS orders,
                ROUND(SUM(order_amount), 2) AS gmv,
                ROUND(SUM(order_amount) / NULLIF(COUNT(*), 0), 2) AS avg_order_value,
                ROUND(
                    SUM(CASE WHEN is_refunded THEN 1 ELSE 0 END)::NUMERIC
                    / NULLIF(COUNT(*), 0),
                    4
                ) AS refund_rate,
                ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction_score
            FROM ecommerce_orders
            WHERE payment_status = 'paid'
            """
        )
    ).mappings().one()

    return {
        "orders": row["orders"],
        "gmv": _to_float(row["gmv"]),
        "avg_order_value": _to_float(row["avg_order_value"]),
        "refund_rate": _to_float(row["refund_rate"]),
        "avg_satisfaction_score": _to_float(row["avg_satisfaction_score"]),
    }


def get_order_summary_by_channel(db: Session) -> list[dict[str, Any]]:
    result = db.execute(
        text(
            """
            SELECT
                channel,
                COUNT(*) AS orders,
                ROUND(SUM(order_amount), 2) AS gmv,
                ROUND(SUM(order_amount) / NULLIF(COUNT(*), 0), 2) AS avg_order_value,
                ROUND(
                    SUM(CASE WHEN is_refunded THEN 1 ELSE 0 END)::NUMERIC
                    / NULLIF(COUNT(*), 0),
                    4
                ) AS refund_rate
            FROM ecommerce_orders
            WHERE payment_status = 'paid'
            GROUP BY channel
            ORDER BY gmv DESC
            """
        )
    )

    return [
        {
            "channel": row["channel"],
            "orders": row["orders"],
            "gmv": _to_float(row["gmv"]),
            "avg_order_value": _to_float(row["avg_order_value"]),
            "refund_rate": _to_float(row["refund_rate"]),
        }
        for row in result.mappings()
    ]


def get_order_summary_by_category(db: Session) -> list[dict[str, Any]]:
    result = db.execute(
        text(
            """
            SELECT
                category,
                COUNT(*) AS orders,
                SUM(quantity) AS quantity,
                ROUND(SUM(order_amount), 2) AS gmv,
                ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction_score
            FROM ecommerce_orders
            WHERE payment_status = 'paid'
            GROUP BY category
            ORDER BY gmv DESC
            """
        )
    )

    return [
        {
            "category": row["category"],
            "orders": row["orders"],
            "quantity": row["quantity"],
            "gmv": _to_float(row["gmv"]),
            "avg_satisfaction_score": _to_float(row["avg_satisfaction_score"]),
        }
        for row in result.mappings()
    ]


def get_recent_orders(db: Session, limit: int = 20) -> list[dict[str, Any]]:
    result = db.execute(
        text(
            """
            SELECT
                order_id,
                order_date,
                city,
                channel,
                category,
                product_name,
                customer_segment,
                quantity,
                unit_price,
                order_amount,
                discount_amount,
                refund_amount,
                is_refunded,
                payment_status,
                satisfaction_score
            FROM ecommerce_orders
            ORDER BY order_date DESC, order_id DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    )

    return [
        {
            "order_id": row["order_id"],
            "order_date": row["order_date"].isoformat(),
            "city": row["city"],
            "channel": row["channel"],
            "category": row["category"],
            "product_name": row["product_name"],
            "customer_segment": row["customer_segment"],
            "quantity": row["quantity"],
            "unit_price": _to_float(row["unit_price"]),
            "order_amount": _to_float(row["order_amount"]),
            "discount_amount": _to_float(row["discount_amount"]),
            "refund_amount": _to_float(row["refund_amount"]),
            "is_refunded": row["is_refunded"],
            "payment_status": row["payment_status"],
            "satisfaction_score": row["satisfaction_score"],
        }
        for row in result.mappings()
    ]
