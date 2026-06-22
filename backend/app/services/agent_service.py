import re
from typing import Any

from sqlalchemy.orm import Session

from app.services.analysis_service import analyze_gmv_change
from app.tools.sql_tools import execute_readonly_sql

CITY_NAMES = ["广州", "深圳", "佛山", "东莞", "珠海", "惠州"]
CHANNEL_NAMES = ["抖音", "小红书", "天猫", "京东", "微信小程序", "线下门店"]
CATEGORY_NAMES = ["美妆", "数码", "服饰", "食品", "家居", "运动"]


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def _extract_first_match(text: str, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in text:
            return candidate
    return None


def _extract_days(text: str, default: int = 14) -> int:
    match = re.search(r"最近\s*(\d+)\s*天", text)
    if not match:
        return default
    return max(1, min(int(match.group(1)), 90))


def _build_where_clause(
    city: str | None,
    channel: str | None,
    category: str | None,
    days: int | None = None,
) -> str:
    clauses = ["payment_status = 'paid'"]
    if days:
        clauses.append(f"order_date >= CURRENT_DATE - INTERVAL '{days} days'")
    if city:
        clauses.append(f"city = '{city}'")
    if channel:
        clauses.append(f"channel = '{channel}'")
    if category:
        clauses.append(f"category = '{category}'")
    return " AND ".join(clauses)


def _summarize_sql_result(intent: str, result: dict[str, Any]) -> str:
    rows = result.get("rows", [])
    if not rows:
        return "没有查询到符合条件的数据。"

    first = rows[0]
    if intent == "city_summary":
        return f"查询完成，GMV 最高的城市是 {first['city']}，GMV 为 {first['gmv']}。"
    if intent == "channel_summary":
        return f"查询完成，GMV 最高的渠道是 {first['channel']}，GMV 为 {first['gmv']}。"
    if intent == "category_summary":
        return f"查询完成，GMV 最高的品类是 {first['category']}，GMV 为 {first['gmv']}。"
    if intent == "recent_orders":
        return f"查询完成，返回最近 {len(rows)} 条订单。"
    return f"查询完成，返回 {len(rows)} 条结果。"


def _build_summary_sql(query: str, limit: int) -> tuple[str, str, dict[str, Any]]:
    city = _extract_first_match(query, CITY_NAMES)
    channel = _extract_first_match(query, CHANNEL_NAMES)
    category = _extract_first_match(query, CATEGORY_NAMES)
    days = _extract_days(query, default=30) if "最近" in query else None
    where_clause = _build_where_clause(city, channel, category, days)

    parameters: dict[str, Any] = {
        "city": city,
        "channel": channel,
        "category": category,
        "days": days,
        "limit": limit,
    }

    if _contains_any(query, ["渠道", "来源"]):
        return (
            "channel_summary",
            f"""
            SELECT
                channel,
                COUNT(*) AS orders,
                ROUND(SUM(order_amount), 2) AS gmv,
                ROUND(SUM(order_amount) / NULLIF(COUNT(*), 0), 2) AS avg_order_value
            FROM ecommerce_orders
            WHERE {where_clause}
            GROUP BY channel
            ORDER BY gmv DESC
            """,
            parameters,
        )

    if _contains_any(query, ["品类", "类目", "商品类型"]):
        return (
            "category_summary",
            f"""
            SELECT
                category,
                COUNT(*) AS orders,
                SUM(quantity) AS quantity,
                ROUND(SUM(order_amount), 2) AS gmv
            FROM ecommerce_orders
            WHERE {where_clause}
            GROUP BY category
            ORDER BY gmv DESC
            """,
            parameters,
        )

    return (
        "city_summary",
        f"""
        SELECT
            city,
            COUNT(*) AS orders,
            ROUND(SUM(order_amount), 2) AS gmv,
            ROUND(SUM(order_amount) / NULLIF(COUNT(*), 0), 2) AS avg_order_value
        FROM ecommerce_orders
        WHERE {where_clause}
        GROUP BY city
        ORDER BY gmv DESC
        """,
        parameters,
    )


def run_agent_query(db: Session, query: str, limit: int = 50) -> dict[str, Any]:
    normalized_query = query.strip()
    city = _extract_first_match(normalized_query, CITY_NAMES)
    current_days = _extract_days(normalized_query, default=14)

    reasoning_steps = [
        "读取用户自然语言问题。",
        "识别问题意图和业务参数。",
    ]

    if _contains_any(normalized_query, ["为什么", "原因", "下降", "上升", "变化"]) and _contains_any(
        normalized_query,
        ["gmv", "GMV", "销售额", "成交额"],
    ):
        reasoning_steps.extend(
            [
                "识别为 GMV 变化归因问题。",
                "选择 analyze_gmv_change 工具进行当前周期和对比周期分析。",
            ]
        )
        result = analyze_gmv_change(
            db,
            current_days=current_days,
            compare_days=current_days,
            city=city,
        )
        return {
            "query": query,
            "intent": "gmv_change_analysis",
            "tool_name": "analyze_gmv_change",
            "parameters": {
                "city": city,
                "current_days": current_days,
                "compare_days": current_days,
            },
            "sql": None,
            "result": result,
            "answer": result["summary"],
            "reasoning_steps": reasoning_steps,
        }

    if _contains_any(normalized_query, ["最近订单", "订单明细", "最近的订单"]):
        sql = """
        SELECT
            order_id,
            order_date,
            city,
            channel,
            category,
            product_name,
            order_amount,
            payment_status
        FROM ecommerce_orders
        ORDER BY order_date DESC, order_id DESC
        """
        result = execute_readonly_sql(db, sql, limit=limit)
        return {
            "query": query,
            "intent": "recent_orders",
            "tool_name": "execute_readonly_sql",
            "parameters": {"limit": limit},
            "sql": result["sql"],
            "result": result,
            "answer": _summarize_sql_result("recent_orders", result),
            "reasoning_steps": reasoning_steps
            + [
                "识别为最近订单查询。",
                "生成只读 SQL 并通过 SQL 工具执行。",
            ],
        }

    intent, sql, parameters = _build_summary_sql(normalized_query, limit)
    result = execute_readonly_sql(db, sql, limit=limit)
    return {
        "query": query,
        "intent": intent,
        "tool_name": "execute_readonly_sql",
        "parameters": parameters,
        "sql": result["sql"],
        "result": result,
        "answer": _summarize_sql_result(intent, result),
        "reasoning_steps": reasoning_steps
        + [
            f"识别为 {intent} 查询。",
            "生成只读 SQL 并通过 SQL 工具执行。",
        ],
    }
