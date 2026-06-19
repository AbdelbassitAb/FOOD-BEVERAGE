-- Test: CUSTOMER_SERVICE_INTERACTIONS_CLEAN
-- Ensure no nulls in key columns and valid satisfaction scores
SELECT *
FROM SILVER.CUSTOMER_SERVICE_INTERACTIONS_CLEAN
WHERE interaction_id IS NULL
   OR interaction_date IS NULL
   OR (customer_satisfaction IS NOT NULL AND (customer_satisfaction < 1 OR customer_satisfaction > 5));