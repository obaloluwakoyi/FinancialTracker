import streamlit as st
from datetime import date
import data_access as da
from modules.expenditure import CATEGORIES as EXP_CATEGORIES
from modules.revenue import CATEGORIES as REV_CATEGORIES


def render(user_id):
    st.header("📋 Budget")
    st.caption("Set monthly budget targets per category, then compare against actuals on the Dashboard.")

    with st.form("add_budget_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            period = st.text_input("Period (YYYY-MM)", value=date.today().strftime("%Y-%m"))
            budget_type = st.selectbox("Type", ["expenditure", "revenue"])
        with c2:
            categories = EXP_CATEGORIES if budget_type == "expenditure" else REV_CATEGORIES
            category = st.selectbox("Category", categories)
        with c3:
            amount = st.number_input("Budgeted Amount (₦)", min_value=0.0, step=1000.0)

        submitted = st.form_submit_button("Save Budget")
        if submitted:
            if amount <= 0:
                st.error("Enter a budgeted amount greater than 0.")
            else:
                da.upsert_budget(user_id, period, budget_type, category, amount)
                st.success(f"Budget saved for {category} ({period}).")
                st.rerun()

    st.divider()
    st.subheader("All Budgets")
    budgets = da.get_budgets(user_id)
    if budgets.empty:
        st.info("No budgets set yet.")
        return

    st.dataframe(
        budgets[["id", "period", "budget_type", "category", "budgeted_amount"]].rename(
            columns={"id": "ID", "period": "Period", "budget_type": "Type",
                     "category": "Category", "budgeted_amount": "Budgeted"}
        ).style.format({"Budgeted": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )

    with st.expander("Delete a budget line"):
        del_id = st.number_input("Budget ID to delete", min_value=0, step=1)
        if st.button("Delete Budget"):
            if del_id > 0:
                da.delete_budget(int(del_id))
                st.success("Deleted.")
                st.rerun()
