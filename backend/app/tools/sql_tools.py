import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

FORBIDDEN_SQL_KEYWORDS = {
    "alter",
    "analyze",
    "call",
    "copy",
    "create",
    "delete",
    "drop",
    "execute",
    "grant",
    "insert",
    "merge",
    "reindex",
    "replace",
    "revoke",
    "truncate",
    "update",
    "vacuum",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date | datetime):
        return value.isoformat()
    return value


def clean_sql(sql: str) -> str:
    return sql.strip().rstrip(";").strip()


def validate_readonly_sql(sql: str) -> tuple[bool, str | None]:
    cleaned = clean_sql(sql)
    lowered = cleaned.lower()

    if not cleaned:
        return False, "SQL must not be empty."

    if ";" in cleaned:
        return False, "Only one SQL statement is allowed."

    if not re.match(r"^(select|with)\b", lowered):
        return False, "Only SELECT or WITH queries are allowed."

    keyword_pattern = r"\b(" + "|".join(sorted(FORBIDDEN_SQL_KEYWORDS)) + r")\b"
    match = re.search(keyword_pattern, lowered)
    if match:
        return False, f"Forbidden SQL keyword: {match.group(1)}."

    return True, None


def get_database_schema(db: Session, table_name: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    table_filter = ""
    if table_name:
        table_filter = "AND c.table_name = :table_name"
        params["table_name"] = table_name

    result = db.execute(
        text(
            f"""
            SELECT
                c.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default
            FROM information_schema.columns c
            WHERE c.table_schema = 'public'
              {table_filter}
            ORDER BY c.table_name, c.ordinal_position
            """
        ),
        params,
    )

    tables: dict[str, list[dict[str, Any]]] = {}
    for row in result.mappings():
        tables.setdefault(row["table_name"], []).append(
            {
                "name": row["column_name"],
                "type": row["data_type"],
                "nullable": row["is_nullable"] == "YES",
                "default": row["column_default"],
            }
        )

    return [
        {
            "table_name": name,
            "columns": columns,
        }
        for name, columns in tables.items()
    ]


def execute_readonly_sql(db: Session, sql: str, limit: int = 50) -> dict[str, Any]:
    cleaned = clean_sql(sql)
    is_valid, reason = validate_readonly_sql(cleaned)
    validation = {
        "is_valid": is_valid,
        "reason": reason,
    }

    if not is_valid:
        return {
            "sql": cleaned,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "validation": validation,
        }

    limited_sql = f"SELECT * FROM ({cleaned}) AS readonly_query LIMIT :limit"
    result = db.execute(text(limited_sql), {"limit": limit})
    rows = [
        {key: _json_safe(value) for key, value in row.items()}
        for row in result.mappings()
    ]
    columns = list(rows[0].keys()) if rows else list(result.keys())

    return {
        "sql": cleaned,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "validation": validation,
    }
