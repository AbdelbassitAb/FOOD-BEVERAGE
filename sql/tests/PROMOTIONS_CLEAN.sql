-- Validation: SILVER.PROMOTIONS_CLEAN
-- This query returns rows with invalid promotion discounts.
SELECT *
FROM SILVER.PROMOTIONS_CLEAN
WHERE discount_percentage IS NULL
   OR discount_percentage < 0
   OR discount_percentage > 1;
