import streamlit as st
from datetime import date
import data_access as da

STATUSES = ["active", "paid_off", "defaulted"]


def render(user_id):
    st.header("🏦 Loans")

    with st.expander("➕ Add Loan", expanded=True):
        with st.form("add_loan_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                loan_date = st.date_input("Loan Date", value=date.today())
                lender = st.text_input("Lender / Borrower Name*")
                loan_type = st.selectbox("Type", ["borrowed", "lent"],
                                          format_func=lambda x: "Borrowed (I owe this)" if x == "borrowed" else "Lent (owed to me)")
            with c2:
                principal_amount = st.number_input("Principal Amount (₦)*", min_value=0.0, step=1000.0)
                interest_rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, step=0.5)
                term_months = st.number_input("Term (months)", min_value=0, step=1)
            purpose = st.selectbox(
                "How the loan will be used",
                ["Business startup", "Inventory / stock purchase", "Equipment / tools", "Working capital", "Other"],
            )
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Add Loan")
            if submitted:
                if not lender or principal_amount <= 0:
                    st.error("Lender/borrower name and a principal greater than 0 are required.")
                else:
                    da.add_loan(user_id, str(loan_date), lender, loan_type, principal_amount,
                                interest_rate, int(term_months) if term_months else None, purpose, notes)
                    st.success(f"Loan with {lender} added.")
                    st.rerun()

    st.divider()
    st.subheader("All Loans")
    loans = da.get_loans(user_id)
    if loans.empty:
        st.info("No loans recorded yet.")
        return

    loans["balance"] = loans.apply(lambda r: da.get_loan_balance(r["id"], r["principal_amount"]), axis=1)

    total_borrowed = loans[loans["loan_type"] == "borrowed"]["balance"].sum()
    total_lent = loans[loans["loan_type"] == "lent"]["balance"].sum()
    c1, c2 = st.columns(2)
    c1.metric("Outstanding Owed by You (Liabilities)", f"₦{total_borrowed:,.2f}")
    c2.metric("Outstanding Owed to You (Receivables)", f"₦{total_lent:,.2f}")

    st.dataframe(
        loans[["id", "loan_date", "lender", "loan_type", "principal_amount", "interest_rate",
               "term_months", "purpose", "balance", "status"]].rename(
            columns={"id": "ID", "loan_date": "Date", "lender": "Lender/Borrower", "loan_type": "Type",
                     "principal_amount": "Principal", "interest_rate": "Rate %", "term_months": "Term (mo)",
                     "purpose": "Use of Funds", "balance": "Balance", "status": "Status"}
        ).style.format({"Principal": "₦{:,.2f}", "Balance": "₦{:,.2f}", "Rate %": "{:.2f}%"}),
        use_container_width=True, hide_index=True
    )

    st.divider()
    st.subheader("Record a Repayment")
    loan_options = {f"{r['lender']} — ₦{r['principal_amount']:,.0f} (ID {r['id']})": r["id"] for _, r in loans.iterrows()}
    selected_label = st.selectbox("Select loan", list(loan_options.keys()))
    selected_id = loan_options[selected_label]

    with st.form("add_payment_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            payment_date = st.date_input("Payment Date", value=date.today())
            amount = st.number_input("Payment Amount (₦)", min_value=0.0, step=100.0)
        with c2:
            notes = st.text_input("Notes")
        submit_payment = st.form_submit_button("Record Payment")
        if submit_payment:
            if amount <= 0:
                st.error("Enter a payment amount greater than 0.")
            else:
                da.add_loan_payment(selected_id, str(payment_date), amount, notes)
                st.success("Payment recorded.")
                st.rerun()

    payments = da.get_loan_payments(selected_id)
    if not payments.empty:
        st.write("**Payment history for selected loan:**")
        st.dataframe(
            payments[["payment_date", "amount", "notes"]].rename(
                columns={"payment_date": "Date", "amount": "Amount", "notes": "Notes"}
            ).style.format({"Amount": "₦{:,.2f}"}),
            use_container_width=True, hide_index=True
        )

    st.divider()
    new_status = st.selectbox("Update status for selected loan", STATUSES)
    if st.button("Update Loan Status"):
        da.update_loan_status(selected_id, new_status)
        st.success("Status updated.")
        st.rerun()
