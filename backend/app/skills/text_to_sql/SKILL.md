# Text-to-SQL Skill

## Goal

Translate a user's business question into a safe read-only SQL query or select a reliable analysis tool.

## When to Use

Use this skill when the user asks about ecommerce order data, including:

- GMV, sales amount, or order amount
- order count
- channel, city, category, or customer segment summaries
- recent order details
- metric changes between time windows

## Available Data

Primary table:

- `ecommerce_orders`

Important fields:

- `order_date`
- `city`
- `province`
- `channel`
- `category`
- `product_name`
- `customer_segment`
- `quantity`
- `order_amount`
- `refund_amount`
- `is_refunded`
- `payment_status`
- `satisfaction_score`

## Metric Definitions

- GMV: `SUM(order_amount)` for paid orders.
- Orders: `COUNT(*)` for paid orders.
- Average order value: `SUM(order_amount) / COUNT(*)`.
- Refund rate: refunded paid orders divided by all paid orders.
- Average satisfaction score: `AVG(satisfaction_score)`.

## Process

1. Identify user intent.
2. Extract filters such as city, channel, category, and time range.
3. If the task is a standard metric-change analysis, call a deterministic analysis tool.
4. If the task is an exploratory query, generate a read-only SQL query.
5. Validate SQL before execution.
6. Execute SQL with a row limit.
7. Summarize the result in business language.

## SQL Safety Rules

- Only `SELECT` or `WITH` queries are allowed.
- Do not generate `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, or other write operations.
- Always filter by `payment_status = 'paid'` when calculating GMV or order metrics.
- Use `LIMIT` for exploratory detail queries.

## Output

Return:

- detected intent
- selected tool
- parameters
- SQL if generated
- structured result
- final natural-language answer
