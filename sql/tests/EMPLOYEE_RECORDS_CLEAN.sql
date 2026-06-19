-- Test: EMPLOYEE_RECORDS_CLEAN
-- Ensure employee ids exist and numeric fields sensible
SELECT *
FROM SILVER.EMPLOYEE_RECORDS_CLEAN
WHERE employee_id IS NULL
   OR hire_date IS NULL
   OR (salary IS NOT NULL AND salary < 0);