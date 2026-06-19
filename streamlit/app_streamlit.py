
################################################################################
##      c'est le code de l'app qui regroupe les autres fichiers 
##      Vous pouvez copier ce code directement dans snowflake et l'executer
################################################################################





import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="AnyCompany • Marketing Analytics", layout="wide")
session = get_active_session()

@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    return session.sql(sql).to_pandas()

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

# ============================================================
# ============================================================
with st.sidebar:
    st.title("AnyCompany")
    st.caption("Marketing Analytics")
    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "📈 Sales",
            "🏷️ Promotions",
            "💰 Marketing ROI",
            "👥 Customers",
            "🚚 Ops & Logistics",
        ],
        index=0
    )
    st.divider()
    st.caption("Sources: ANYCOMPANY_LAB.SILVER")

# ============================================================
# APP HEADER
# ============================================================
st.title("AnyCompany • Data-Driven Marketing Analytics")

# ============================================================
# PAGES
# ============================================================
def overview_page():
    st.subheader("Overview — KPIs & visualisations rapides")

    # --- KPIs (global)
    kpi = run_query("""
    SELECT
      SUM(IFF(transaction_type='Sale', amount, 0)) AS total_sales,
      COUNT_IF(transaction_type='Sale') AS nb_sales,
      COUNT(DISTINCT region) AS nb_regions
    FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN;
    """)

    total_sales = safe_float(kpi.loc[0, "TOTAL_SALES"]) if not kpi.empty else 0.0
    nb_sales = safe_int(kpi.loc[0, "NB_SALES"]) if not kpi.empty else 0
    nb_regions = safe_int(kpi.loc[0, "NB_REGIONS"]) if not kpi.empty else 0

    promo_rate_df = run_query("""
    WITH sales AS (
      SELECT transaction_id, transaction_date, region
      FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
      WHERE transaction_type='Sale'
    ),
    flagged AS (
      SELECT
        s.*,
        IFF(EXISTS (
          SELECT 1
          FROM SILVER.PROMOTIONS_CLEAN p
          WHERE p.region = s.region
            AND s.transaction_date BETWEEN p.start_date AND p.end_date
        ), 1, 0) AS is_promo
      FROM sales s
    )
    SELECT AVG(is_promo)::FLOAT AS promo_rate
    FROM flagged;
    """)
    promo_rate = safe_float(promo_rate_df.loc[0, "PROMO_RATE"]) if not promo_rate_df.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", fmt_money(total_sales))
    c2.metric("Number of sales (Sale)", f"{nb_sales:,}".replace(",", " "))
    c3.metric("Number of regions", f"{nb_regions:,}".replace(",", " "))
    c4.metric("Share of sales during promo period", f"{promo_rate*100:.1f}%")

    st.divider()

    # --- Quick charts
    df_month = run_query("""
    SELECT DATE_TRUNC('month', transaction_date) AS month,
           SUM(amount) AS total_sales
    FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
    WHERE transaction_type='Sale'
    GROUP BY month
    ORDER BY month;
    """)

    df_regions = run_query("""
    SELECT region, SUM(amount) AS total_sales
    FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
    WHERE transaction_type='Sale'
    GROUP BY region
    ORDER BY total_sales DESC;
    """)

    left, right = st.columns(2)

    with left:
        st.caption("Sales trend (monthly) — line chart")
        if not df_month.empty:
            df_month["MONTH"] = pd.to_datetime(df_month["MONTH"])
            st.line_chart(df_month.set_index("MONTH")[["TOTAL_SALES"]])
        else:
            st.info("No sales data.")

    with right:
        st.caption("Sales by region — bar chart")
        if not df_regions.empty:
            st.bar_chart(df_regions.set_index("REGION")[["TOTAL_SALES"]])
        else:
            st.info("No regional data.")

    with st.expander("View data (overview)"):
        st.write("Sales by month:")
        st.dataframe(df_month, use_container_width=True)
        st.write("Sales by region:")
        st.dataframe(df_regions, use_container_width=True)


def sales_page():
    st.subheader("Sales — tendances & sanity checks")

    df_month = run_query("""
    SELECT DATE_TRUNC('month', transaction_date) AS month,
           SUM(amount) AS total_sales,
           COUNT(*) AS nb_sales
    FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
    WHERE transaction_type='Sale'
    GROUP BY month
    ORDER BY month;
    """)

    if not df_month.empty:
        df_month["MONTH"] = pd.to_datetime(df_month["MONTH"])

        st.caption("Total Sales (monthly) — line chart")
        st.line_chart(df_month.set_index("MONTH")[["TOTAL_SALES"]])

        st.caption("Number of sales (monthly) — line chart")
        st.line_chart(df_month.set_index("MONTH")[["NB_SALES"]])
    else:
        st.info("No sales data.")

    st.divider()

    # Transaction type distribution (sanity check)
    df_types = run_query("""
    SELECT transaction_type, SUM(amount) AS total_amount
    FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
    GROUP BY transaction_type
    ORDER BY total_amount DESC;
    """)

    st.caption("Total amount by transaction type — bar chart")
    if not df_types.empty:
        st.bar_chart(df_types.set_index("TRANSACTION_TYPE")[["TOTAL_AMOUNT"]])
    else:
        st.info("No transaction type data.")

    with st.expander("View tables (sales)"):
        st.dataframe(df_month, use_container_width=True)
        st.dataframe(df_types, use_container_width=True)


def promotions_page():
    st.subheader("Promotions — volume & discount")

    # Promotions by category (best chart)
    df_cat = run_query("""
    SELECT
      product_category,
      COUNT(*) AS nb_promos,
      AVG(discount_percentage) AS avg_discount
    FROM SILVER.PROMOTIONS_CLEAN
    GROUP BY product_category
    ORDER BY nb_promos DESC;
    """)

    c1, c2 = st.columns(2)

    with c1:
        st.caption("Number of promotions by category — bar chart")
        if not df_cat.empty:
            st.bar_chart(df_cat.set_index("PRODUCT_CATEGORY")[["NB_PROMOS"]])
        else:
            st.info("No promotion data by category.")

    with c2:
        st.caption("Average discount by category — bar chart")
        if not df_cat.empty:
            # avg_discount is between 0 and 1 in your cleaning rules
            st.bar_chart(df_cat.set_index("PRODUCT_CATEGORY")[["AVG_DISCOUNT"]])
        else:
            st.info("No discount data.")

    st.divider()

    df_region = run_query("""
    SELECT region, COUNT(*) AS nb_promos
    FROM SILVER.PROMOTIONS_CLEAN
    GROUP BY region
    ORDER BY nb_promos DESC;
    """)

    st.caption("Number of promotions by region — bar chart")
    if not df_region.empty:
        st.bar_chart(df_region.set_index("REGION")[["NB_PROMOS"]])

    with st.expander("View tables (promotions)"):
        st.dataframe(df_cat, use_container_width=True)
        st.dataframe(df_region, use_container_width=True)


def roi_page():
    st.subheader("Marketing ROI — campaign analysis (proxy)")

    df_roi = run_query("""
    SELECT
      campaign_name,
      region,
      product_category,
      budget,
      reach,
      conversion_rate,
      (reach * conversion_rate) AS estimated_conversions,
      (reach * conversion_rate) / NULLIF(budget, 0) AS roi_proxy
    FROM SILVER.MARKETING_CAMPAIGNS_CLEAN
    ORDER BY roi_proxy DESC
    LIMIT 50;
    """)

    st.caption("Top campaigns by proxy ROI — bar chart")
    if not df_roi.empty:
        st.bar_chart(df_roi.head(20).set_index("CAMPAIGN_NAME")[["ROI_PROXY"]])
    else:
        st.info("No campaign data.")

    st.divider()

    # Campaign sales during campaign period
    df_campaign_sales = run_query("""
    WITH sales_daily AS (
      SELECT transaction_date, region, SUM(amount) AS daily_sales
      FROM SILVER.FINANCIAL_TRANSACTIONS_CLEAN
      WHERE transaction_type='Sale'
      GROUP BY transaction_date, region
    )
    SELECT
      c.campaign_name,
      c.region,
      SUM(s.daily_sales) AS sales_during_campaign
    FROM SILVER.MARKETING_CAMPAIGNS_CLEAN c
    LEFT JOIN sales_daily s
      ON s.region = c.region
     AND s.transaction_date BETWEEN c.start_date AND c.end_date
    GROUP BY c.campaign_name, c.region
    ORDER BY sales_during_campaign DESC NULLS LAST
    LIMIT 50;
    """)

    st.caption("Top campaigns by sales during campaign — bar chart")
    if not df_campaign_sales.empty:
        st.bar_chart(df_campaign_sales.head(20).set_index("CAMPAIGN_NAME")[["SALES_DURING_CAMPAIGN"]])
    else:
        st.info("No campaign sales data.")

    with st.expander("View tables (ROI)"):
        st.dataframe(df_roi, use_container_width=True)
        st.dataframe(df_campaign_sales, use_container_width=True)


def customers_page():
    st.subheader("Customers — descriptive segmentation & customer experience")

    df_region = run_query("""
    SELECT region, COUNT(*) AS nb_clients, AVG(annual_income) AS avg_income
    FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
    GROUP BY region
    ORDER BY nb_clients DESC;
    """)
    df_gender = run_query("""
    SELECT gender, COUNT(*) AS nb_clients
    FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
    GROUP BY gender
    ORDER BY nb_clients DESC;
    """)
    df_marital = run_query("""
    SELECT marital_status, COUNT(*) AS nb_clients
    FROM SILVER.CUSTOMER_DEMOGRAPHICS_CLEAN
    GROUP BY marital_status
    ORDER BY nb_clients DESC;
    """)
    df_service = run_query("""
    SELECT issue_category,
           AVG(customer_satisfaction) AS avg_satisfaction,
           COUNT(*) AS nb_interactions
    FROM SILVER.CUSTOMER_SERVICE_INTERACTIONS_CLEAN
    GROUP BY issue_category
    ORDER BY avg_satisfaction ASC;
    """)

    left, right = st.columns(2)

    with left:
        st.caption("Customers by region — bar chart")
        if not df_region.empty:
            st.bar_chart(df_region.set_index("REGION")[["NB_CLIENTS"]])
        st.caption("Customers by gender — bar chart")
        if not df_gender.empty:
            st.bar_chart(df_gender.set_index("GENDER")[["NB_CLIENTS"]])

    with right:
        st.caption("Customers by marital status — bar chart")
        if not df_marital.empty:
            st.bar_chart(df_marital.set_index("MARITAL_STATUS")[["NB_CLIENTS"]])
        st.caption("Average satisfaction by issue category — bar chart")
        if not df_service.empty:
            st.bar_chart(df_service.set_index("ISSUE_CATEGORY")[["AVG_SATISFACTION"]])

    st.divider()

    df_reviews = run_query("""
    SELECT product_category,
           AVG(rating) AS avg_rating,
           COUNT(*) AS nb_reviews
    FROM SILVER.PRODUCT_REVIEWS_CLEAN
    GROUP BY product_category
    ORDER BY avg_rating DESC;
    """)

    st.caption("Product reviews: average rating by category — bar chart")
    if not df_reviews.empty:
        st.bar_chart(df_reviews.set_index("PRODUCT_CATEGORY")[["AVG_RATING"]])

    with st.expander("View tables (customers)"):
        st.dataframe(df_region, use_container_width=True)
        st.dataframe(df_gender, use_container_width=True)
        st.dataframe(df_marital, use_container_width=True)
        st.dataframe(df_service, use_container_width=True)
        st.dataframe(df_reviews, use_container_width=True)


def ops_page():
    st.subheader("Ops & Logistics — stock alerts & delivery")

    # Stock alerts by category
    df_stock_cat = run_query("""
    SELECT product_category, COUNT(*) AS nb_stock_alerts
    FROM SILVER.INVENTORY_CLEAN
    WHERE current_stock IS NOT NULL
      AND reorder_point IS NOT NULL
      AND current_stock <= reorder_point
    GROUP BY product_category
    ORDER BY nb_stock_alerts DESC;
    """)

    # Delivery days by status
    df_delivery = run_query("""
    SELECT status,
           AVG(DATEDIFF('day', ship_date, estimated_delivery)) AS avg_delivery_days,
           COUNT(*) AS nb_shipments
    FROM SILVER.LOGISTICS_AND_SHIPPING_CLEAN
    WHERE ship_date IS NOT NULL
      AND estimated_delivery IS NOT NULL
    GROUP BY status
    ORDER BY avg_delivery_days DESC;
    """)

    left, right = st.columns(2)

    with left:
        st.caption("Stock alerts by category — bar chart")
        if not df_stock_cat.empty:
            st.bar_chart(df_stock_cat.set_index("PRODUCT_CATEGORY")[["NB_STOCK_ALERTS"]])
        else:
            st.info("No stock alerts detected.")

    with right:
        st.caption("Average delivery days by status — bar chart")
        if not df_delivery.empty:
            st.bar_chart(df_delivery.set_index("STATUS")[["AVG_DELIVERY_DAYS"]])
        else:
            st.info("No delivery data.")

    with st.expander("View tables (ops)"):
        st.dataframe(df_stock_cat, use_container_width=True)
        st.dataframe(df_delivery, use_container_width=True)


# ============================================================
# ROUTER
# ============================================================
if page == "🏠 Overview":
    overview_page()
elif page == "📈 Sales":
    sales_page()
elif page == "🏷️ Promotions":
    promotions_page()
elif page == "💰 Marketing ROI":
    roi_page()
elif page == "👥 Customers":
    customers_page()
else:
    ops_page()

