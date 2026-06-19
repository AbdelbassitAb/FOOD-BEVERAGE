-- Validation: SILVER.INVENTORY_CLEAN
-- This query returns rows WITH invalid inventory VALUES.
SELECT *
FROM SILVER.INVENTORY_CLEAN
WHERE current_stock < 0
   OR reorder_point < 0
   OR lead_time < 0;
