import streamlit as st
from datetime import date
import pandas as pd
import data_access as da


def render(user_id):
    st.header("🧾 All-in-One History")
    st.caption("See the full performance story of your business in one place.")

    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("From", value=date.today().replace(day=1), key="hist_start")
    with c2:
        end_date = st.date_input("To", value=date.today(), key="hist_end")

    sales_df = da.get_sales(user_id, str(start_date), str(end_date))
    exp_df = da.get_expenditures(user_id, str(start_date), str(end_date))
    rev_df = da.get_revenues(user_id, str(start_date), str(end_date))
    loans = da.get_loans(user_id)

    history_rows = []
    if not sales_df.empty:
        for _, row in sales_df.iterrows():
            history_rows.append({"Date": row["sale_date"], "Type": "Sales", "Description": row.get("customer_name") or "Sale", "Amount": row["total_amount"], "Direction": "Income"})
    if not rev_df.empty:
        for _, row in rev_df.iterrows():
            history_rows.append({"Date": row["rev_date"], "Type": "Revenue", "Description": row["source"], "Amount": row["amount"], "Direction": "Income"})
    if not exp_df.empty:
        for _, row in exp_df.iterrows():
            history_rows.append({"Date": row["exp_date"], "Type": "Expense", "Description": row["category"], "Amount": row["amount"], "Direction": "Expense"})
    if not loans.empty:
        for _, row in loans.iterrows():
            history_rows.append({"Date": row["loan_date"], "Type": "Loan", "Description": f"{row['lender']} ({row['purpose'] or 'loan'})", "Amount": row["principal_amount"], "Direction": "Liability"})

    if not history_rows:
        st.info("No activity recorded in this period yet.")
        return

    history_df = pd.DataFrame(history_rows)
    history_df = history_df.sort_values("Date", ascending=False)
    st.dataframe(
        history_df.rename(columns={"Date": "Date", "Type": "Type", "Description": "Description", "Amount": "Amount", "Direction": "Direction"})
        .style.format({"Amount": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )

    total_income = history_df.loc[history_df["Direction"].isin(["Income"]), "Amount"].sum()
    total_expenses = history_df.loc[history_df["Direction"].isin(["Expense"]), "Amount"].sum()
    net = total_income - total_expenses

    c1, c2, c3 = st.columns(3)
    c1.metric("Income", f"₦{total_income:,.2f}")
    c2.metric("Expenses", f"₦{total_expenses:,.2f}")
    c3.metric("Net Performance", f"₦{net:,.2f}", delta="Positive" if net >= 0 else "Negative")
