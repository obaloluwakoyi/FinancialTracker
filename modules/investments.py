import streamlit as st
from datetime import date
import data_access as da

INV_TYPES = ["Stocks", "Bonds", "Real Estate", "Fixed Deposit", "Treasury Bills", "Mutual Fund",
             "Business Equity", "Cryptocurrency", "Other"]
STATUSES = ["active", "matured", "closed", "written_off"]


def render(user_id):
    st.header("📈 Investments")

    with st.expander("➕ Add Investment", expanded=True):
        with st.form("add_inv_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                inv_date = st.date_input("Investment Date", value=date.today())
                name = st.text_input("Investment Name*")
                inv_type = st.selectbox("Type", INV_TYPES)
            with c2:
                amount = st.number_input("Amount Invested (₦)*", min_value=0.0, step=1000.0)
                expected_return = st.number_input("Expected Return (₦, optional)", min_value=0.0, step=1000.0)
                current_value = st.number_input("Current Value (₦, optional)", min_value=0.0, step=1000.0)
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Add Investment")
            if submitted:
                if not name or amount <= 0:
                    st.error("Name and an amount greater than 0 are required.")
                else:
                    cv = current_value if current_value > 0 else amount
                    da.add_investment(user_id, str(inv_date), name, inv_type, amount,
                                       expected_return or None, cv, "active", notes)
                    st.success(f"Investment '{name}' added.")
                    st.rerun()

    st.divider()
    st.subheader("Portfolio")
    invs = da.get_investments(user_id)
    if invs.empty:
        st.info("No investments recorded yet.")
        return

    invs["gain_loss"] = invs["current_value"] - invs["amount"]
    total_invested = invs["amount"].sum()
    total_current = invs["current_value"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invested", f"₦{total_invested:,.2f}")
    c2.metric("Current Portfolio Value", f"₦{total_current:,.2f}")
    c3.metric("Unrealized Gain/Loss", f"₦{total_current - total_invested:,.2f}")

    st.dataframe(
        invs[["id", "inv_date", "name", "inv_type", "amount", "current_value", "gain_loss", "status"]].rename(
            columns={"id": "ID", "inv_date": "Date", "name": "Name", "inv_type": "Type",
                     "amount": "Invested", "current_value": "Current Value",
                     "gain_loss": "Gain/Loss", "status": "Status"}
        ).style.format({"Invested": "₦{:,.2f}", "Current Value": "₦{:,.2f}", "Gain/Loss": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )

    st.divider()
    st.subheader("Update Investment")
    inv_options = {f"{r['name']} (ID {r['id']})": r["id"] for _, r in invs.iterrows()}
    selected_label = st.selectbox("Select investment", list(inv_options.keys()))
    selected_id = inv_options[selected_label]

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        new_value = st.number_input("New current value (₦)", min_value=0.0, step=1000.0)
    with c2:
        new_status = st.selectbox("Status", STATUSES)
    with c3:
        st.write("")
        st.write("")
        if st.button("Update"):
            da.update_investment_status(selected_id, new_status, new_value if new_value > 0 else None)
            st.success("Investment updated.")
            st.rerun()

    if st.button("🗑️ Delete this investment"):
        da.delete_investment(selected_id)
        st.success("Deleted.")
        st.rerun()
