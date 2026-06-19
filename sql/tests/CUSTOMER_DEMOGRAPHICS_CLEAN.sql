-- Test: CUSTOMER_DEMOGRAPHICS_CLEAN
-- Ensure key identifiers present and age/income sensible
SELECT *
FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
WHERE customer_id IS NULL
   OR birth_date IS NULL
   OR (age IS NOT NULL AND (age < 0 OR age > 120))
   OR (annual_income IS NOT NULL AND annual_income < 0);