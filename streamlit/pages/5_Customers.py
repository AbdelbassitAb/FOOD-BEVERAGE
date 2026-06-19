import streamlit as st
from _utils import run_query

st.title("👥 Customers")
st.caption("Descriptive segmentation & customer experience")

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

df_service["AVG_SATISFACTION"] = df_service["AVG_SATISFACTION"].astype(float)


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


with st.expander("View tables"):
    st.dataframe(df_region, use_container_width=True)
    st.dataframe(df_gender, use_container_width=True)
    st.dataframe(df_marital, use_container_width=True)
    st.dataframe(df_service, use_container_width=True)
