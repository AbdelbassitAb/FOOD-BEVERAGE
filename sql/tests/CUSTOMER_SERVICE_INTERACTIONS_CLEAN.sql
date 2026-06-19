-- Test: CUSTOMER_SERVICE_INTERACTIONS_CLEAN
-- Ensure no nulls in key columns and valid satisfaction scores
SELECT *
FROM SILVER.CUSTOMER_SERVICE_INTERACTIONS_CLEAN
WHERE interaction_id IS NULL
   OR customer_id IS NULL
   OR interaction_date IS NULL
   OR (satisfaction_score IS NOT NULL AND (satisfaction_score < 0 OR satisfaction_score > 10));