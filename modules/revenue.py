import streamlit as st
from datetime import date
import data_access as da

CATEGORIES = ["Sales", "Service Income", "Interest Income", "Grants", "Investment Returns", "Other"]


def render(user_id):
    st.header("💰 Revenue")
    st.info("Revenue is generated automatically from completed sales. Manual revenue entries are disabled.")
    st.caption("Record sales on the Sales page and the dashboard will reflect the revenue from those transactions.")

    st.divider()
    st.subheader("Revenue from Completed Sales")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("From", value=date.today().replace(day=1), key="rev_start")
    with c2:
        end_date = st.date_input("To", value=date.today(), key="rev_end")

    sales_df = da.get_sales(user_id, str(start_date), str(end_date))
    if sales_df.empty:
        st.info("No sales have been recorded in this period yet.")
        return

    total_sales_revenue = sales_df["total_amount"].sum()
    st.metric("Revenue from Sales", f"₦{total_sales_revenue:,.2f}")
    st.dataframe(
        sales_df[["sale_date", "customer_name", "payment_method", "total_amount", "notes"]].rename(
            columns={"sale_date": "Date", "customer_name": "Customer", "payment_method": "Payment",
                     "total_amount": "Total", "notes": "Notes"}
        ).style.format({"Total": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )
