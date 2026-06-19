-- 2.2 – Descriptive exploratory analysis (SQL)
-- 2.2.1 Sales evolution over time

SELECT
  DATE_TRUNC('month', transaction_date) AS month,
  SUM(amount) AS total_sales,
  COUNT(*) AS nb_sales
FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
WHERE transaction_type = 'Sale'
GROUP BY month
ORDER BY month;

-- 2.2.2 Performance by category and region (proxy)

-- Sales by region

SELECT
  region,
  SUM(amount) AS total_sales,
  COUNT(*) AS nb_sales
FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
WHERE transaction_type = 'Sale'
GROUP BY region
ORDER BY total_sales DESC;

-- Sales by transaction type (sanity check)

SELECT transaction_type, COUNT(*) AS cnt, SUM(amount) AS total_amount
FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- 2.2.3 Customer distribution by demographic segments

-- By region

SELECT region, COUNT(*) AS nb_clients, AVG(annual_income) AS avg_income
FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
GROUP BY region
ORDER BY nb_clients DESC;

-- By gender

SELECT gender, COUNT(*) AS nb_clients
FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
GROUP BY gender
ORDER BY nb_clients DESC;

-- By marital status

SELECT marital_status, COUNT(*) AS nb_clients
FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
GROUP BY marital_status
ORDER BY nb_clients DESC;
