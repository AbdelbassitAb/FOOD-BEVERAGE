-- Test: MARKETING_CAMPAIGNS_CLEAN
-- Ensure no nulls in key columns and budgets are positive
SELECT *
FROM SILVER.MARKETING_CAMPAIGNS_CLEAN
WHERE campaign_id IS NULL
   OR start_date IS NULL
   OR end_date IS NULL
   OR budget IS NULL
   OR budget <= 0;