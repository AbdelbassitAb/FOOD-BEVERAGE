import os
import streamlit as st
import pandas as pd
import snowflake.connector

# ------------------------------------------------------------
# Snowflake connection configuration
# ------------------------------------------------------------


def load_snowflake_config():
    if "snowflake" in st.secrets:
        return st.secrets["snowflake"]

    env_cfg = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    }

    if env_cfg["account"] and env_cfg["user"] and env_cfg["password"]:
        return env_cfg

    raise KeyError(
        "Snowflake credentials not found. Set st.secrets['snowflake'] or the environment variables "
        "SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_WAREHOUSE, "
        "SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA."
    )


@st.cache_resource
def get_conn():
    cfg = load_snowflake_config()
    conn = snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        role=cfg.get("role"),
        warehouse=cfg.get("warehouse"),
        database=cfg.get("database"),
        schema=cfg.get("schema"),
    )
    return conn


# ------------------------------------------------------------
# Helper SQL
# ------------------------------------------------------------
@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        return cur.fetch_pandas_all()
    finally:
        cur.close()


# ------------------------------------------------------------
# Helpers formatting & casting
# ------------------------------------------------------------
def safe_float(x, default=0.0):
    try:
        return default if x is None else float(x)
    except:
        return default


def safe_int(x, default=0):
    try:
        return default if x is None else int(x)
    except:
        return default


def fmt_money(x: float) -> str:
    try:
        return f"{x:,.0f}".replace(",", " ")
    except:
        return str(x)
