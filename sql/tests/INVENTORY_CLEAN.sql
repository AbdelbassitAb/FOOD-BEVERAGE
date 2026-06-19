-- This query returns rows with invalid inventory values.
SELECT *
FROM SILVER.INVENTORY_CLEAN
WHERE current_stock < 0
   OR reorder_point < 0
   OR lead_time < 0;
