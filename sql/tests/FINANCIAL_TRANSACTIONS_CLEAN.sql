-- Validation: SILVER.FINANCIAL_TRANSACTIONS_CLEAN
-- This query returns rows WITH invalid transaction amounts.
SELECT *
FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
WHERE amount IS NULL
   OR amount <= 0;
