# ML Implementation Guide

This guide describes how the ML training script in `streamlit/ml_models/promo_optimizer.py` works and how to run it.

## What it does

- Connects to Snowflake using credentials from environment variables or `streamlit/.streamlit/secrets.toml`.
- Loads the prepared ML feature table `ANALYTICS.ML_PROMO_EFFECTIVENESS`.
- Cleans and encodes features.
- Trains a Gradient Boosting model for promotion ROI and effectiveness.
- Prints training output and saves the model artifacts.

## Requirements

- Python dependencies from `requirements.txt`
- Snowflake connection configured via environment variables or `streamlit/.streamlit/secrets.toml`.
- The ML feature tables created in Snowflake by running `sql/phase_3/2_ml_feature_tables.sql`.

## Configuration

Use one of the following methods:

1. Create `streamlit/.streamlit/secrets.toml` with a `[snowflake]` section.
2. Or set environment variables:
   - `SNOWFLAKE_ACCOUNT`
   - `SNOWFLAKE_USER`
   - `SNOWFLAKE_PASSWORD`
   - `SNOWFLAKE_WAREHOUSE`
   - `SNOWFLAKE_DATABASE`
   - `SNOWFLAKE_SCHEMA`

If both are available, environment variables take precedence.

## Running the ML script

```bash
python streamlit/ml_models/promo_optimizer.py
```

If the table `ANALYTICS.ML_PROMO_EFFECTIVENESS` does not exist, the script prints a clear error and points to `sql/phase_3/2_ml_feature_tables.sql`.

## Notes

- The script is designed as a standalone training entrypoint.
- It uses the Snowflake Python connector and pandas to load data into memory.
- It does not rotate or manage Snowflake credentials; those must be handled outside the codebase.
