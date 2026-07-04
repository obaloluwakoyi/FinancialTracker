import streamlit as st
from datetime import date
import data_access as da


def render(user_id):
    st.header("⚙️ Operations")
    st.caption("Track how money is used for business growth, analyst support, and loan repayments.")

    with st.expander("💼 Pay AI Analyst", expanded=True):
        with st.form("pay_analyst_form", clear_on_submit=True):
            if "analyst_date" not in st.session_state:
                st.session_state.analyst_date = date.today()
            if "analyst_amount" not in st.session_state:
                st.session_state.analyst_amount = 0.0
            if "analyst_notes" not in st.session_state:
                st.session_state.analyst_notes = ""

            pay_date = st.date_input("Payment Date", key="analyst_date", value=st.session_state.analyst_date)
            amount = st.number_input("Amount (₦)", min_value=0.0, step=100.0, key="analyst_amount")
            notes = st.text_area("Notes", key="analyst_notes")
            submitted, clear_form = st.columns([1, 1])
            with submitted:
                submitted = st.form_submit_button("Record Payment")
            with clear_form:
                clear_clicked = st.form_submit_button("Clear")

            if submitted:
                if amount <= 0:
                    st.error("Enter an amount greater than 0.")
                else:
                    da.add_expenditure(user_id, str(pay_date), "AI Analyst", notes or "AI analyst payment", amount, "Bank Transfer")
                    st.success("AI analyst payment recorded.")
                    st.rerun()
            if clear_clicked:
                st.session_state.analyst_date = date.today()
                st.session_state.analyst_amount = 0.0
                st.session_state.analyst_notes = ""
                st.rerun()

    st.divider()
    st.subheader("Loan Repayment / Business Use")
    loans = da.get_loans(user_id)
    if loans.empty:
        st.info("Add a loan first on the Loans page to track repayment usage.")
    else:
        loan_options = {f"{r['lender']} — ₦{r['principal_amount']:,.0f} (ID {r['id']})": r['id'] for _, r in loans.iterrows()}
        selected_label = st.selectbox("Select loan", list(loan_options.keys()))
        selected_id = loan_options[selected_label]
        with st.form("loan_use_form", clear_on_submit=True):
            if "loan_payment_date" not in st.session_state:
                st.session_state.loan_payment_date = date.today()
            if "loan_payment_amount" not in st.session_state:
                st.session_state.loan_payment_amount = 0.0
            if "loan_payment_purpose" not in st.session_state:
                st.session_state.loan_payment_purpose = "Loan repayment"

            payment_date = st.date_input("Repayment Date", value=st.session_state.loan_payment_date, key="loan_payment_date")
            amount = st.number_input("Repayment Amount (₦)", min_value=0.0, step=100.0, key="loan_payment_amount")
            purpose = st.text_input("Purpose of this payment", key="loan_payment_purpose")
            submit_col, clear_col = st.columns([1, 1])
            with submit_col:
                submitted = st.form_submit_button("Record Repayment")
            with clear_col:
                clear_clicked = st.form_submit_button("Clear")
            if submitted:
                if amount <= 0:
                    st.error("Enter an amount greater than 0.")
                else:
                    da.add_loan_payment(selected_id, str(payment_date), amount, purpose)
                    st.success("Loan repayment recorded.")
                    st.rerun()
            if clear_clicked:
                st.session_state.loan_payment_date = date.today()
                st.session_state.loan_payment_amount = 0.0
                st.session_state.loan_payment_purpose = "Loan repayment"
                st.rerun()

    st.divider()
    st.subheader("Operations Summary")
    exp_df = da.get_expenditures(user_id, str(date.today().replace(day=1)), str(date.today()))
    if exp_df.empty:
        st.info("No operations expenses recorded yet.")
        return

    summary = exp_df[exp_df["category"].isin(["AI Analyst", "Loan Repayment", "Business Startup", "Inventory", "Equipment", "Working Capital"])]
    if summary.empty:
        st.info("No matching operations entries found.")
        return

    st.dataframe(
        summary[["exp_date", "category", "description", "amount", "payment_method"]].rename(
            columns={"exp_date": "Date", "category": "Category", "description": "Description", "amount": "Amount", "payment_method": "Payment Method"}
        ).style.format({"Amount": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )
