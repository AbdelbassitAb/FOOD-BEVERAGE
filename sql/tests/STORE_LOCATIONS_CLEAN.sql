-- Test: STORE_LOCATIONS_CLEAN
-- Ensure store identifiers and basic numeric sanity checks
SELECT *
FROM SILVER.STORE_LOCATIONS_CLEAN
WHERE store_id IS NULL
   OR address IS NULL
   OR (square_footage IS NOT NULL AND square_footage <= 0)
   OR (employee_count IS NOT NULL AND employee_count < 0);