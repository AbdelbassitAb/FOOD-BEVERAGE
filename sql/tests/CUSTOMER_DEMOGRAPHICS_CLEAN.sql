-- Test: CUSTOMER_DEMOGRAPHICS_CLEAN
-- Ensure key identifiers present and age/income sensible
SELECT *
FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
WHERE customer_id IS NULL
   OR date_of_birth IS NULL
   OR (annual_income IS NOT NULL AND annual_income < 0);