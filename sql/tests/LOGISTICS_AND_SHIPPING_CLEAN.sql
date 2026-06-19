-- This query returns rows with invalid shipping costs.
SELECT *
FROM SILVER.LOGISTICS_AND_SHIPPING_CLEAN
WHERE shipping_cost IS NULL
   OR shipping_cost < 0;
