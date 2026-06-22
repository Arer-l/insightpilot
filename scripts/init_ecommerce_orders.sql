DROP TABLE IF EXISTS ecommerce_orders;

CREATE TABLE ecommerce_orders (
    order_id BIGSERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    city VARCHAR(32) NOT NULL,
    province VARCHAR(32) NOT NULL,
    channel VARCHAR(32) NOT NULL,
    category VARCHAR(32) NOT NULL,
    product_name VARCHAR(80) NOT NULL,
    customer_segment VARCHAR(32) NOT NULL,
    customer_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    order_amount NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(10, 2) NOT NULL,
    refund_amount NUMERIC(10, 2) NOT NULL,
    is_refunded BOOLEAN NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    satisfaction_score INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO ecommerce_orders (
    order_date,
    city,
    province,
    channel,
    category,
    product_name,
    customer_segment,
    customer_id,
    quantity,
    unit_price,
    order_amount,
    discount_amount,
    refund_amount,
    is_refunded,
    payment_status,
    satisfaction_score
)
SELECT
    order_date,
    city,
    province,
    channel,
    category,
    product_name,
    customer_segment,
    customer_id,
    quantity,
    unit_price,
        ROUND(quantity * unit_price * anomaly_factor - discount_amount, 2) AS order_amount,
    discount_amount,
    CASE
        WHEN is_refunded THEN ROUND((quantity * unit_price * anomaly_factor - discount_amount) * refund_ratio, 2)
        ELSE 0
    END AS refund_amount,
    is_refunded,
    payment_status,
    satisfaction_score
FROM (
    SELECT
        (CURRENT_DATE - order_day_offset) AS order_date,
        city,
        province,
        channel,
        category,
        product_name,
        customer_segment,
        customer_id,
        quantity,
        unit_price,
        discount_amount,
        is_refunded,
        refund_ratio,
        payment_status,
        satisfaction_score,
        CASE
            WHEN city = '广州'
                AND channel = '抖音'
                AND category = '美妆'
                AND (CURRENT_DATE - order_day_offset) >= (CURRENT_DATE - 14)
            THEN 0.58::NUMERIC
            WHEN city = '深圳'
                AND channel = '小红书'
                AND category = '数码'
                AND (CURRENT_DATE - order_day_offset) >= (CURRENT_DATE - 10)
            THEN 1.32::NUMERIC
            ELSE 1.00::NUMERIC
        END AS anomaly_factor
    FROM (
        SELECT
            gs,
            (random() * 89)::INT AS order_day_offset,
            CASE (random() * 5)::INT
                WHEN 0 THEN '广州'
                WHEN 1 THEN '深圳'
                WHEN 2 THEN '佛山'
                WHEN 3 THEN '东莞'
                WHEN 4 THEN '珠海'
                ELSE '惠州'
            END AS city,
            '广东' AS province,
            CASE (random() * 5)::INT
                WHEN 0 THEN '抖音'
                WHEN 1 THEN '小红书'
                WHEN 2 THEN '天猫'
                WHEN 3 THEN '京东'
                WHEN 4 THEN '微信小程序'
                ELSE '线下门店'
            END AS channel,
            CASE (random() * 5)::INT
                WHEN 0 THEN '美妆'
                WHEN 1 THEN '数码'
                WHEN 2 THEN '服饰'
                WHEN 3 THEN '食品'
                WHEN 4 THEN '家居'
                ELSE '运动'
            END AS category,
            CASE (random() * 5)::INT
                WHEN 0 THEN '明星单品A'
                WHEN 1 THEN '新品套装B'
                WHEN 2 THEN '会员专享C'
                WHEN 3 THEN '高客单D'
                WHEN 4 THEN '清仓款E'
                ELSE '基础款F'
            END AS product_name,
            CASE (random() * 3)::INT
                WHEN 0 THEN '新客'
                WHEN 1 THEN '普通老客'
                WHEN 2 THEN '高价值会员'
                ELSE '沉睡召回'
            END AS customer_segment,
            10000 + (random() * 5000)::INT AS customer_id,
            1 + (random() * 4)::INT AS quantity,
            ROUND((39 + random() * 760)::NUMERIC, 2) AS unit_price,
            ROUND((random() * 80)::NUMERIC, 2) AS discount_amount,
            random() < 0.08 AS is_refunded,
            (0.35 + random() * 0.65)::NUMERIC AS refund_ratio,
            CASE
                WHEN random() < 0.94 THEN 'paid'
                WHEN random() < 0.98 THEN 'pending'
                ELSE 'failed'
            END AS payment_status,
            CASE
                WHEN random() < 0.08 THEN 1 + (random() * 2)::INT
                ELSE 3 + (random() * 2)::INT
            END AS satisfaction_score
        FROM generate_series(1, 1500) AS gs
    ) seed
) enriched;

CREATE INDEX idx_ecommerce_orders_date ON ecommerce_orders(order_date);
CREATE INDEX idx_ecommerce_orders_city ON ecommerce_orders(city);
CREATE INDEX idx_ecommerce_orders_channel ON ecommerce_orders(channel);
CREATE INDEX idx_ecommerce_orders_category ON ecommerce_orders(category);

SELECT COUNT(*) AS total_orders FROM ecommerce_orders;
