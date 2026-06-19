-- Test: SUPPLIER_INFORMATION_CLEAN
-- Ensure supplier ids exist and important contact fields present
SELECT *
FROM SILVER.SUPPLIER_INFORMATION_CLEAN
WHERE supplier_id IS NULL
   OR supplier_name IS NULL
   OR contact_email IS NULL;