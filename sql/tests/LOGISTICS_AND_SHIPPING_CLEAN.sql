-- Validation: SILVER.LOGISTICS_AND_SHIPPING_CLEAN
-- This query returns rows WITH invalid shipping costs.
SELECT *
FROM SILVER.LOGISTICS_AND_SHIPPING_CLEAN
WHERE shipping_cost IS NULL
   OR shipping_cost < 0;
