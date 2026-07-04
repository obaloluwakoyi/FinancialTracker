import streamlit as st
from datetime import date
import data_access as da

CATEGORIES = ["Rent", "Utilities", "Salaries", "Inventory/Supplies", "Marketing",
              "Transport/Logistics", "Equipment", "Loan Repayment", "Taxes", "Other"]


def render(user_id):
    st.header("💸 Expenditure")

    with st.expander("➕ Add Expenditure", expanded=True):
        with st.form("add_exp_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                exp_date = st.date_input("Date", value=date.today())
                category = st.selectbox("Category", CATEGORIES)
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Card", "POS", "Other"])
            with c2:
                amount = st.number_input("Amount (₦)*", min_value=0.0, step=100.0)
                description = st.text_area("Description")

            submitted = st.form_submit_button("Add Expenditure")
            if submitted:
                if amount <= 0:
                    st.error("Amount must be greater than 0.")
                else:
                    da.add_expenditure(user_id, str(exp_date), category, description, amount, payment_method)
                    st.success("Expenditure recorded.")
                    st.rerun()

    st.divider()
    st.subheader("Expenditure History")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("From", value=date.today().replace(day=1), key="exp_start")
    with c2:
        end_date = st.date_input("To", value=date.today(), key="exp_end")

    exp_df = da.get_expenditures(user_id, str(start_date), str(end_date))
    if exp_df.empty:
        st.info("No expenditure records in this period.")
        return

    st.write(f"**Total: ₦{exp_df['amount'].sum():,.2f}**")
    st.dataframe(
        exp_df[["id", "exp_date", "category", "description", "amount", "payment_method"]].rename(
            columns={"id": "ID", "exp_date": "Date", "category": "Category", "description": "Description",
                     "amount": "Amount", "payment_method": "Payment"}
        ).style.format({"Amount": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )

    with st.expander("Delete a record"):
        del_id = st.number_input("Expenditure ID to delete", min_value=0, step=1)
        if st.button("Delete Expenditure"):
            if del_id > 0:
                da.delete_expenditure(int(del_id))
                st.success("Deleted.")
                st.rerun()
