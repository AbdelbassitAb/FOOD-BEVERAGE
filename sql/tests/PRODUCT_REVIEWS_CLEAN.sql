-- Validation: SILVER.PRODUCT_REVIEWS_CLEAN
-- This query returns rows with invalid review ratings.
SELECT *
FROM SILVER.PRODUCT_REVIEWS_CLEAN
WHERE rating IS NULL
   OR rating < 1
   OR rating > 5;
