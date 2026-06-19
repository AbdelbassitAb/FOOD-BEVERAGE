-- ============================================================================
-- Phase 3.2 - ML feature table for Promo Optimizer
-- Purpose: create feature table for promo ROI prediction
-- Created: 2026-01-31 | Fixed for actual schema
-- ============================================================================

USE DATABASE ANYCOMPANY_LAB;
USE SCHEMA ANALYTICS;

-- ============================================================================
-- ml_promo_effectiveness: training data for promo ROI optimizer
-- ============================================================================

CREATE OR REPLACE TABLE ANALYTICS.ML_PROMO_EFFECTIVENESS AS
WITH promo_sales AS (
    -- Calculate sales during each promotion
    SELECT
        p.promotion_id,
        p.product_category,
        p.start_date,
        p.end_date,
        p.discount_percentage,
        p.promotion_type,
        p.region,
        DATEDIFF(day, p.start_date, p.end_date) + 1 AS duration_days,

        -- Sales during promo (from financial transactions where type = 'Sale')
        COUNT(DISTINCT t.transaction_id) AS transactions_count,
        SUM(t.amount) AS total_sales,
        AVG(t.amount) AS avg_transaction_value

    FROM SILVER.PROMOTIONS_CLEAN p
    LEFT JOIN SILVER.FINANCIAL_TRANSACTIONS_CLEAN t
        ON t.transaction_date BETWEEN p.start_date AND p.end_date
        AND t.region = p.region
        AND t.transaction_type = 'Sale'
    GROUP BY 1,2,3,4,5,6,7,8
),
baseline_sales AS (
    -- Calculate baseline sales (30 days before promo, same region)
    SELECT
        p.promotion_id,
        AVG(t.amount) AS baseline_avg_transaction,
        COUNT(DISTINCT t.transaction_id) / 30.0 AS baseline_daily_transactions,
        SUM(t.amount) / 30.0 AS baseline_daily_sales

    FROM SILVER.PROMOTIONS_CLEAN p
    LEFT JOIN SILVER.FINANCIAL_TRANSACTIONS_CLEAN t
        ON t.transaction_date BETWEEN DATEADD(day, -30, p.start_date)
            AND DATEADD(day, -1, p.start_date)
        AND t.region = p.region
        AND t.transaction_type = 'Sale'
    GROUP BY p.promotion_id
),
campaign_overlap AS (
    -- Check if promo overlaps with campaigns
    SELECT
        p.promotion_id,
        MAX(CASE WHEN c.campaign_id IS NOT NULL THEN 1 ELSE 0 END) AS has_campaign_overlap,
        COUNT(DISTINCT c.campaign_id) AS num_overlapping_campaigns
    FROM SILVER.PROMOTIONS_CLEAN p
    LEFT JOIN SILVER.MARKETING_CAMPAIGNS_CLEAN c
        ON c.region = p.region
        AND (c.start_date <= p.end_date AND c.end_date >= p.start_date)
    GROUP BY p.promotion_id
),
seasonality AS (
    -- Add temporal features
    SELECT
        promotion_id,
        EXTRACT(MONTH FROM start_date) AS start_month,
        EXTRACT(QUARTER FROM start_date) AS start_quarter,
        DAYOFWEEK(start_date) AS start_day_of_week,
        CASE
            WHEN EXTRACT(MONTH FROM start_date) IN (11, 12) THEN 1
            ELSE 0
        END AS is_holiday_season,
        CASE
            WHEN DAYOFWEEK(start_date) IN (0, 6) THEN 1
            ELSE 0
        END AS starts_on_weekend
    FROM SILVER.PROMOTIONS_CLEAN
)

SELECT
    ps.promotion_id,
    ps.product_category,
    ps.promotion_type,
    ps.region,
    ps.discount_percentage,
    ps.duration_days,
    ps.start_date,
    ps.end_date,

    -- Sales metrics
    ps.transactions_count,
    ps.total_sales,
    ps.avg_transaction_value,

    -- Baseline comparison
    COALESCE(bs.baseline_avg_transaction, 0) AS baseline_avg_transaction,
    COALESCE(bs.baseline_daily_transactions, 0) AS baseline_daily_transactions,
    COALESCE(bs.baseline_daily_sales, 0) AS baseline_daily_sales,

    -- Campaign context
    COALESCE(co.has_campaign_overlap, 0) AS has_campaign_overlap,
    COALESCE(co.num_overlapping_campaigns, 0) AS num_overlapping_campaigns,

    -- Temporal features
    s.start_month,
    s.start_quarter,
    s.start_day_of_week,
    s.is_holiday_season,
    s.starts_on_weekend,

    -- Target variables (ROI proxies)
    CASE
        WHEN bs.baseline_daily_sales > 0
        THEN ((ps.total_sales / ps.duration_days) - bs.baseline_daily_sales) / bs.baseline_daily_sales
        ELSE 0
    END AS sales_lift_ratio,

    CASE
        WHEN ps.total_sales > bs.baseline_daily_sales * ps.duration_days
        THEN 1
        ELSE 0
    END AS is_successful,

    -- Estimated promo cost (proxy: discount × sales volume)
    ps.total_sales * ps.discount_percentage AS estimated_promo_cost,

    -- ROI proxy = (incremental sales) / (estimated cost)
    CASE
        WHEN ps.total_sales * ps.discount_percentage > 0
        THEN (ps.total_sales - (bs.baseline_daily_sales * ps.duration_days)) /
                 (ps.total_sales * ps.discount_percentage)
        ELSE 0
    END AS roi_proxy

FROM promo_sales ps
LEFT JOIN baseline_sales bs ON ps.promotion_id = bs.promotion_id
LEFT JOIN campaign_overlap co ON ps.promotion_id = co.promotion_id
LEFT JOIN seasonality s ON ps.promotion_id = s.promotion_id
WHERE bs.baseline_daily_sales IS NOT NULL;  -- Only keep promos with baseline data

-- ============================================================================
-- Verification
-- ============================================================================

SELECT
    'ML_PROMO_EFFECTIVENESS created successfully!' AS status,
    COUNT(*) AS total_promos,
    AVG(sales_lift_ratio) AS avg_sales_lift,
    SUM(is_successful) AS successful_promos,
    ROUND(AVG(roi_proxy), 2) AS avg_roi_proxy
FROM ANALYTICS.ML_PROMO_EFFECTIVENESS;

-- Grant permissions
GRANT SELECT ON TABLE ANALYTICS.ML_PROMO_EFFECTIVENESS TO ROLE SYSADMIN;

SELECT '✅ Setup complete! Ready to train ML models.' AS next_step;
