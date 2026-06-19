# AnyCompany Food & Beverage – Data-Driven Marketing Analytics (Snowflake + Streamlit + ML)

Project completed as part of the **Data-Driven Marketing Analytics with Snowflake and Streamlit** workshop.  
Goal: build a reliable analytics foundation (ingestion + cleaning), produce business-ready analyses, and industrialize those insights as a **data product** ready for BI and Machine Learning.

## 🔐 Snowflake access

This project does not include live Snowflake credentials. Configure your own connection in `streamlit/.streamlit/secrets.toml` or use environment variables.

- **URL** : set via `streamlit/.streamlit/secrets.toml` or environment variables
- **Login** : set via `streamlit/.streamlit/secrets.toml` or environment variables
- **Password** : set via `streamlit/.streamlit/secrets.toml` or environment variables
- **Database** : set via `streamlit/.streamlit/secrets.toml` or environment variables
- **Warehouse** : set via `streamlit/.streamlit/secrets.toml` or environment variables

## 1) Business context & objectives

AnyCompany (fictitious company) is facing:

- a decline in sales over the last fiscal year,
- a 30% reduction in marketing budget,
- a loss of market share (28% → 22% in 8 months).

**Objective**: shift marketing toward a data-driven strategy to:

- reverse the trend,
- target **+10 market share points** (22% → 32%) by Q4 2025,
- optimize actions with a reduced budget.

---

## 2) Architecture and approach

The architecture is built as a 3-layer design:

- **BRONZE**: raw data from CSV/JSON files
- **SILVER**: cleaned, consistent, and usable data
- **ANALYTICS**: data product (stable tables with KPIs and useful flags)

Data source: `s3://logbrain-datalake/datasets/food-beverage/`

---

## 3) Phase 1 – Data Preparation & Ingestion (Snowflake)

### 3.1 Step 1 — Snowflake environment setup

#### 3.1.1 Warehouse creation

An `XSMALL` warehouse was used to limit credit consumption, with auto-suspend enabled.

```sql
CREATE OR REPLACE WAREHOUSE WH_LAB
WITH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

USE WAREHOUSE WH_LAB;
```

#### 3.1.2 Create database and schemas

A dedicated lab database was created, along with 3 schemas:

- `BRONZE` (raw)
- `SILVER` (clean)
- `ANALYTICS` (data product)

```sql
CREATE OR REPLACE DATABASE ANYCOMPANY_LAB;

CREATE OR REPLACE SCHEMA ANYCOMPANY_LAB.BRONZE;
CREATE OR REPLACE SCHEMA ANYCOMPANY_LAB.SILVER;
CREATE OR REPLACE SCHEMA ANYCOMPANY_LAB.ANALYTICS;
```

---

### 3.2 Step 2 — File formats & S3 stage

#### 3.2.1 File formats

**Standard CSV** (comma delimiter):

```sql
CREATE OR REPLACE FILE FORMAT FF_CSV
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  TRIM_SPACE = TRUE
  NULL_IF = ('', 'NULL');
```

**TSV (tab-delimited)**: used for `product_reviews.csv` because the file was actually tab-separated.  
Without this setting, the error _"Number of columns in file does not match table"_ occurred.  
`ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE` was added to avoid a complete load failure.

```sql
CREATE OR REPLACE FILE FORMAT FF_TSV
  TYPE = CSV
  FIELD_DELIMITER = '\t'
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  TRIM_SPACE = TRUE
  NULL_IF = ('', 'NULL', 'null')
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;
```

**JSON**: the supplied JSON files were arrays, so `STRIP_OUTER_ARRAY = TRUE` was required.

```sql
CREATE OR REPLACE FILE FORMAT FF_JSON
  TYPE = JSON
  STRIP_OUTER_ARRAY = TRUE;
```

#### 3.2.2 S3 Stage

```sql
CREATE OR REPLACE STAGE STG_FOOD_BEVERAGE
  URL = 's3://logbrain-datalake/datasets/food-beverage/'
  FILE_FORMAT = FF_CSV;

LIST @STG_FOOD_BEVERAGE;
```

---

### 3.3 Step 2 — Create BRONZE tables (raw)

A BRONZE table was created for each file.  
For JSON files, we stored the records in a `raw VARIANT` column.

Examples:

- **CSV**: types adapted for analysis (DATE, NUMBER(18,2), etc.)
- **JSON**: `raw VARIANT` table

```sql
CREATE OR REPLACE TABLE BRONZE.INVENTORY_RAW ( raw VARIANT );
CREATE OR REPLACE TABLE BRONZE.STORE_LOCATIONS_RAW ( raw VARIANT );
```

---

### 3.4 Step 3 — Load data (COPY INTO)

For each BRONZE table, data was loaded from the S3 stage using `COPY INTO` with the appropriate `FILE_FORMAT`.

Examples:

```sql
COPY INTO BRONZE.CUSTOMER_DEMOGRAPHICS
FROM @STG_FOOD_BEVERAGE/customer_demographics.csv
FILE_FORMAT = (FORMAT_NAME = FF_CSV)
ON_ERROR = 'CONTINUE';
```

`product_reviews.csv` (TSV):

```sql
COPY INTO BRONZE.PRODUCT_REVIEWS
FROM @STG_FOOD_BEVERAGE/product_reviews.csv
FILE_FORMAT = (FORMAT_NAME = FF_TSV)
ON_ERROR = 'CONTINUE';
```

JSON:

```sql
COPY INTO BRONZE.INVENTORY_RAW
FROM @STG_FOOD_BEVERAGE/inventory.json
FILE_FORMAT = (FORMAT_NAME = FF_JSON)
ON_ERROR = 'CONTINUE';
```

#### COPY verification (history)

```sql
SELECT *
FROM TABLE(
  INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME=>'FINANCIAL_TRANSACTIONS',
    START_TIME=>DATEADD('hour', -2, CURRENT_TIMESTAMP())
  )
);
```

---

### 3.5 Step 4 — Post-load checks (BRONZE)

After each load, we systematically:

- checked **volumes** (empty table / partial load),
- reviewed a **sample** (`LIMIT 10`),
- identified **key columns** (IDs, dates, regions, categories),
- detected obvious anomalies (negative values, invalid dates, etc.).

Example global volume check:

```sql
SELECT 'CUSTOMER_DEMOGRAPHICS' AS table_name, COUNT(*) AS nb_rows FROM BRONZE.CUSTOMER_DEMOGRAPHICS
UNION ALL SELECT 'FINANCIAL_TRANSACTIONS', COUNT(*) FROM BRONZE.FINANCIAL_TRANSACTIONS
UNION ALL SELECT 'STORE_LOCATIONS_RAW', COUNT(*) FROM BRONZE.STORE_LOCATIONS_RAW
ORDER BY table_name;
```

---

## 4) Phase 1 – Step 5: Data Cleaning (BRONZE → SILVER)

### 4.1 Applied cleaning principles

For each BRONZE table, a SILVER table was created using:

1. **Text cleanup**
   - `TRIM()`, `NULLIF(TRIM(x), '')` to avoid empty strings
2. **Type harmonization**
   - Dates: `TRY_TO_DATE(...)`
   - Numerics: `TRY_TO_DECIMAL(...)`, removing spaces with `REPLACE(x,' ','')`
3. **Quality rules**
   - positive amounts (transactions)
   - discount between 0 and 1 (promotions)
   - rating between 1 and 5 (reviews)
   - shipping costs >= 0
   - lead_time, stock, reorder_point >= 0
4. **Duplicate handling (IDs)**
   - General rule: **if an ID should be unique, deduplicate it**
   - Method: `QUALIFY ROW_NUMBER()` using a business rule (most recent date or most complete row)
5. **Remove rows with region 0 and 1 in the PROMOTIONS table**

---

### 4.2 Example: Financial Transactions

**Objective**: secure the sales base with usable amounts, unique IDs, and valid dates.

- Deduplicate on `transaction_id`
- Robust amount conversion
- Remove null or negative amounts

```sql
CREATE OR REPLACE TABLE SILVER.FINANCIAL_TRANSACTIONS_CLEAN AS
SELECT
  TRIM(transaction_id) AS transaction_id,
  TRY_TO_DATE(transaction_date::VARCHAR) AS transaction_date,
  TRIM(transaction_type) AS transaction_type,
  TRY_TO_DECIMAL(REPLACE(amount::VARCHAR, ' ', ''), 18, 2) AS amount,
  TRIM(payment_method) AS payment_method,
  TRIM(entity) AS entity,
  NULLIF(TRIM(region), '') AS region,
  TRIM(account_code) AS account_code
FROM BRONZE.FINANCIAL_TRANSACTIONS
WHERE transaction_id IS NOT NULL AND TRIM(transaction_id) <> ''
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY TRIM(transaction_id)
  ORDER BY TRY_TO_DATE(transaction_date::VARCHAR) DESC NULLS LAST
) = 1;

DELETE FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
WHERE amount IS NULL OR amount <= 0;
```

---

### 4.3 Example: Promotions

- validate the period (`start_date <= end_date`)
- discount between 0 and 1
- remove rows with region 0 and 1

```sql
CREATE OR REPLACE TABLE SILVER.PROMOTIONS_CLEAN AS
SELECT
  TRIM(promotion_id) AS promotion_id,
  NULLIF(TRIM(product_category), '') AS product_category,
  NULLIF(TRIM(promotion_type), '') AS promotion_type,
  TRY_TO_DOUBLE(discount_percentage) AS discount_percentage,
  TRY_TO_DATE(start_date::VARCHAR) AS start_date,
  TRY_TO_DATE(end_date::VARCHAR) AS end_date,
  NULLIF(TRIM(region), '') AS region
FROM BRONZE.PROMOTIONS_DATA
WHERE promotion_id IS NOT NULL
  AND TRIM(promotion_id) <> ''
  AND TRY_TO_DATE(start_date::VARCHAR) IS NOT NULL
  AND TRY_TO_DATE(end_date::VARCHAR) IS NOT NULL
  AND TRY_TO_DATE(start_date::VARCHAR) <= TRY_TO_DATE(end_date::VARCHAR)
  AND TRY_TO_DOUBLE(discount_percentage) BETWEEN 0 AND 1
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY TRIM(promotion_id)
  ORDER BY TRY_TO_DATE(start_date::VARCHAR) DESC NULLS LAST
) = 1;
```

---

### 4.4 Important special case: STORE_LOCATIONS (duplicated IDs)

#### Observation

In `BRONZE.STORE_LOCATIONS_RAW`, there were about **5000 rows**.  
After cleaning and deduplicating by `store_id`, only **897 rows** remained, meaning **~82% of rows were removed**.

This indicates that:

- `store_id` values were heavily duplicated,
- BUT rows with the same `store_id` had **different values** (so these were not true duplicates).

#### Alternative approaches considered

We considered more advanced approaches:

1. **Change the identifier**

- create a technical surrogate key: `store_id + hash(address + city + country)`
- this preserves all rows

2. **Create versions (SCD Type 2)**

- keep history with `valid_from / valid_to`
- requires a reliable date field (for example `updated_at`)

#### Why these were not selected

The workshop data is **synthetic** and does not include a reliable date field (e.g. `updated_at`) to manage versions correctly.  
Without a date, it is impossible to know:

- which row is the “current” version
- which row is the “historical” version

#### Final decision

We chose a simple approach aligned with the learning objective:

✅ **Deduplicate on `store_id` while keeping the most complete row**  
(using `completeness_score` + `ROW_NUMBER()`)

```sql
CREATE OR REPLACE TABLE SILVER.STORE_LOCATIONS_CLEAN AS
WITH parsed AS (
  SELECT
    NULLIF(TRIM(raw:store_id::STRING), '') AS store_id,
    NULLIF(TRIM(raw:store_name::STRING), '') AS store_name,
    NULLIF(TRIM(raw:store_type::STRING), '') AS store_type,
    NULLIF(TRIM(raw:region::STRING), '') AS region,
    NULLIF(TRIM(raw:country::STRING), '') AS country,
    NULLIF(TRIM(raw:city::STRING), '') AS city,
    NULLIF(TRIM(raw:address::STRING), '') AS address,
    NULLIF(TRIM(raw:postal_code::STRING), '') AS postal_code,
    IFF(TRY_TO_DOUBLE(raw:square_footage::STRING) > 0,
        TRY_TO_DOUBLE(raw:square_footage::STRING),
        NULL) AS square_footage,
    IFF(TRY_TO_NUMBER(raw:employee_count::STRING) >= 0,
        TRY_TO_NUMBER(raw:employee_count::STRING),
        NULL) AS employee_count,
    (
      IFF(NULLIF(TRIM(raw:store_name::STRING), '') IS NULL, 0, 1) +
      IFF(NULLIF(TRIM(raw:country::STRING), '') IS NULL, 0, 1) +
      IFF(NULLIF(TRIM(raw:city::STRING), '') IS NULL, 0, 1) +
      IFF(TRY_TO_DOUBLE(raw:square_footage::STRING) > 0, 1, 0) +
      IFF(TRY_TO_NUMBER(raw:employee_count::STRING) >= 0, 1, 0)
    ) AS completeness_score
  FROM BRONZE.STORE_LOCATIONS_RAW
)
SELECT
  store_id, store_name, store_type, region, country, city, address, postal_code,
  square_footage, employee_count
FROM parsed
WHERE store_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY store_id
  ORDER BY completeness_score DESC
) = 1;
```

---

## 5) Phase 2 – Exploratory & business analysis (SILVER)

The analyses were performed using SILVER tables, covering:

- sales trends over time,
- regional performance,
- promotion impact (by region + period),
- campaign proxy ROI,
- ratings by category,
- customer service (satisfaction),
- stock outages,
- delivery lead times.

The SQL scripts are grouped in `sql/` (one file per analysis).

---

## 6) Phase 3 – Data Product (ANALYTICS)

### Objective

Industrialize the Phase 2 insights into **reusable analytical tables** that are stable and ready to be consumed by:

- dashboards (Streamlit / BI),
- advanced analytics,
- Machine Learning models.

This phase is an **Analytics Engineering** effort: turning ad hoc analyses into **durable data products**.

---

### Tables created in the `ANALYTICS` schema

#### `ANALYTICS.SALES_ENRICHED`

**Business goal**  
Centralize sales and enrich them with marketing indicators to measure the real impact of:

- promotions,
- marketing campaigns,
- time.

**Contents**

- Sales data (transaction, date, region, amount)
- Analytical flags:
  - promotion period
  - campaign period
- Time-based variables (month, day of week)

**Use cases**

- marketing ROI analysis
- sales comparison with/without promotion
- base for sales forecasting models

**Source tables used**

- `SILVER.FINANCIAL_TRANSACTIONS_CLEAN`
- `SILVER.PROMOTIONS_CLEAN`
- `SILVER.MARKETING_CAMPAIGNS_CLEAN`

---

#### `ANALYTICS.ACTIVE_PROMOTIONS`

**Business goal**  
Provide a normalized table of promotions to analyze their effectiveness by:

- product category,
- region,
- duration.

**Contents**

- promotion, category, region
- applied discount
- start and end dates
- promotion duration (in days)

**Use cases**

- promotion sensitivity analysis
- promotional calendar optimization

**Source tables used**

- `SILVER.PROMOTIONS_CLEAN`

---

#### `ANALYTICS.CUSTOMERS_ENRICHED`

**Business goal**  
Create an enriched customer table to enable **advanced marketing segmentation**.

**Contents**

- demographic information
- calculated age
- income segment (Low / Medium / High)

**Use cases**

- marketing targeting
- customer scoring
- base for churn or customer value models

**Source tables used**

- `SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN`

---

### Example: creating `ANALYTICS.SALES_ENRICHED`

```sql
CREATE OR REPLACE TABLE ANALYTICS.SALES_ENRICHED AS
WITH sales AS (
  SELECT transaction_id, transaction_date, region, amount
  FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
  WHERE transaction_type = 'Sale'
),
promo_flag AS (
  SELECT s.transaction_id, MAX(1) AS is_promo_period
  FROM sales s
  JOIN SILVER.PROMOTIONS_CLEAN p
    ON s.region = p.region
   AND s.transaction_date BETWEEN p.start_date AND p.end_date
  GROUP BY s.transaction_id
),
campaign_flag AS (
  SELECT s.transaction_id, MAX(1) AS is_campaign_period
  FROM sales s
  JOIN SILVER.MARKETING_CAMPAIGNS_CLEAN c
    ON s.region = c.region
   AND s.transaction_date BETWEEN c.start_date AND c.end_date
  GROUP BY s.transaction_id
)
SELECT
  s.transaction_id,
  s.transaction_date,
  s.region,
  s.amount,
  COALESCE(p.is_promo_period, 0) AS is_promo_period,
  COALESCE(c.is_campaign_period, 0) AS is_campaign_period,
  DATE_TRUNC('month', s.transaction_date) AS sales_month,
  DAYOFWEEK(s.transaction_date) AS day_of_week
FROM sales s
LEFT JOIN promo_flag p ON s.transaction_id = p.transaction_id
LEFT JOIN campaign_flag c ON s.transaction_id = c.transaction_id;
```

### Phase 3 results

At the end of this phase, the project has:

- a **coherent analytical data product**, built from cleaned and validated data;
- **documented, reusable analytical tables** centralized in the `ANALYTICS` schema;
- a **ready-to-use data foundation** for:
  - dashboards with **Streamlit**,
  - advanced marketing analytics (ROI, segmentation, campaign performance),
  - marketing-oriented Machine Learning models (customer segmentation, propensity, promotion response).

---

## 7) Streamlit (dashboards)

One page per analysis (Streamlit multi-page app):

- Sales Dashboard
- Promotion Analysis
- Marketing ROI
- Customer Segmentation
- Operations & Logistics

Snowflake connection via `.streamlit/secrets.toml` (not versioned).

---

## 8) Project structure

```text
SNOWFLAKE/
├── ml/
├── sql/
│ ├── phase_1/
│ │ ├── 1_environment_setup.sql
│ │ ├── 2_create_tables.sql
│ │ ├── 3_load_data.sql
│ │ ├── 4_verify_load.sql
│ │ └── 5_clean_data.sql
│ ├── phase_2/
│ │ ├── 1_data_understanding.sql
│ │ ├── 2_descriptive_exploratory_analysis.sql
│ │ ├── 3.1_promotion_impact.sql
│ │ ├── 3.2_campaign_performance.sql
│ │ ├── 3.3_customer_experience.sql
│ │ └── 3.4_operations_and_logistics.sql
│ └── phase_3/
│   ├── 1_create_data_product.sql
│   └── 2_ml_feature_tables.sql
├── streamlit/
│ ├── .streamlit/
│ │ ├── config.toml
│ │ └── secrets.toml.example
│ ├── ml_models/
│ ├── pages/
│ ├── _utils.py
│ ├── check_databases.py
│ ├── check_sql_ready.py
│ └── Home.py
├── business_insights.md
├── README.md
└── requirements.txt
```

---

## 9) AI-Powered Promo Planning - Predict promotion ROI before launch with ML models!

---

## 🚀 Quick Start - Run the ML Demo

```powershell
# 1. Create ML feature tables in Snowflake
# Execute: sql/phase_3/2_ml_feature_tables.sql

# 2. Train ML models (2 minutes)
python streamlit/ml_models/promo_optimizer.py

# 3. Launch Streamlit
cd streamlit
python -m streamlit run Home.py

# 4. Navigate to "7_Promo_Planner" and predict ROI!
```

📖 **Full ML Guide**: See `ML_IMPLEMENTATION_README.md`

---

## 10) Notes and limitations

- The data is **synthetic**, so some keys (e.g. `store_id`) do not always reflect realistic business logic.
- `customer_id` is missing from transactions, so sales and customer analyses remain separate.
- `product_id` is missing from sales, so product analyses are done by proxy (category/region/period).

---

## 11) Run the Streamlit app

From the `streamlit` folder:

```bash
streamlit run Home.py
```

Or you can copy the full app code available in the file `streamlit/app_streamlit.py` directly into Snowflake.
This file contains all requested pages in a single app.

---
