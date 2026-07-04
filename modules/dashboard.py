import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
import data_access as da
from modules.ai_helper import get_recommendations


def render(user_id):
    st.markdown(
        """
        <div class="page-title">
            <h1>📊 Dashboard</h1>
            <p>A quick overview of your financial health for the selected period.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today().replace(day=1), key="dash_start")
    with col2:
        end_date = st.date_input("To", value=date.today(), key="dash_end")

    s_str, e_str = str(start_date), str(end_date)

    sales_df = da.get_sales(user_id, s_str, e_str)
    exp_df = da.get_expenditures(user_id, s_str, e_str)
    rev_df = da.get_revenues(user_id, s_str, e_str)
    sale_items_df = da.get_sale_profit_summary(user_id, s_str, e_str)

    sales_total = sales_df["total_amount"].sum() if not sales_df.empty else 0
    other_revenue_total = rev_df["amount"].sum() if not rev_df.empty else 0
    total_revenue = sales_total + other_revenue_total
    total_expenditure = exp_df["amount"].sum() if not exp_df.empty else 0

    cogs = 0
    if not sale_items_df.empty:
        cogs = (sale_items_df["cost_price"] * sale_items_df["quantity"]).sum()

    gross_profit = sales_total - cogs
    net_profit = total_revenue - total_expenditure - cogs

    loans = da.get_loans(user_id)
    outstanding_loans = loans[loans["status"] == "active"]["principal_amount"].sum() if not loans.empty else 0
    cash_remaining = total_revenue - total_expenditure

    # ---- KPI cards ----
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue", f"₦{total_revenue:,.2f}")
    c2.metric("Total Expenditure", f"₦{total_expenditure:,.2f}")
    c3.metric("Cash Remaining", f"₦{cash_remaining:,.2f}")
    c4.metric("COGS (from sales)", f"₦{cogs:,.2f}")
    c5.metric("Net Profit / Loss", f"₦{net_profit:,.2f}",
              delta=f"{'Profit' if net_profit >= 0 else 'Loss'}")

    st.divider()
    with st.container():
        st.subheader("AI Recommendations")
        recs = get_recommendations({
            "net_profit": net_profit,
            "total_revenue": total_revenue,
            "total_expenditure": total_expenditure,
            "cogs": cogs,
            "sales_total": sales_total,
            "outstanding_loans": outstanding_loans,
        })
        for item in recs:
            st.write(f"• {item}")

    st.divider()

    # ---- Revenue vs Expenditure trend ----
    st.subheader("Revenue vs Expenditure Over Time")
    if not sales_df.empty or not exp_df.empty or not rev_df.empty:
        rev_daily = pd.DataFrame()
        if not sales_df.empty:
            rev_daily = sales_df.groupby("sale_date")["total_amount"].sum().reset_index()
            rev_daily.columns = ["date", "sales_revenue"]
        other_daily = pd.DataFrame()
        if not rev_df.empty:
            other_daily = rev_df.groupby("rev_date")["amount"].sum().reset_index()
            other_daily.columns = ["date", "other_revenue"]
        exp_daily = pd.DataFrame()
        if not exp_df.empty:
            exp_daily = exp_df.groupby("exp_date")["amount"].sum().reset_index()
            exp_daily.columns = ["date", "expenditure"]

        merged = pd.DataFrame({"date": []})
        for d in [rev_daily, other_daily, exp_daily]:
            if not d.empty:
                merged = pd.merge(merged, d, on="date", how="outer")
        merged = merged.fillna(0).sort_values("date")

        fig = go.Figure()
        if "sales_revenue" in merged.columns:
            fig.add_trace(go.Scatter(x=merged["date"], y=merged["sales_revenue"], name="Sales Revenue", mode="lines+markers"))
        if "other_revenue" in merged.columns:
            fig.add_trace(go.Scatter(x=merged["date"], y=merged["other_revenue"], name="Other Revenue", mode="lines+markers"))
        if "expenditure" in merged.columns:
            fig.add_trace(go.Scatter(x=merged["date"], y=merged["expenditure"], name="Expenditure", mode="lines+markers"))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No revenue or expenditure records in this period yet.")

    # ---- Expenditure breakdown ----
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Expenditure by Category")
        if not exp_df.empty:
            by_cat = exp_df.groupby("category")["amount"].sum().reset_index()
            fig2 = px.pie(by_cat, names="category", values="amount", hole=0.4)
            fig2.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("No expenditure records yet.")

    with col_b:
        st.subheader("Top Selling Products")
        if not sale_items_df.empty:
            top = sale_items_df.groupby("product_name")["subtotal"].sum().reset_index().sort_values(
                "subtotal", ascending=False).head(8)
            fig3 = px.bar(top, x="product_name", y="subtotal")
            fig3.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.caption("No sales records yet.")

    st.divider()

    # ---- Budget vs Actual ----
    st.subheader("Budget vs Actual (current period)")
    period_str = date.today().strftime("%Y-%m")
    budgets = da.get_budgets(user_id, period_str)
    if budgets.empty:
        st.caption(f"No budget set for {period_str} yet. Go to the Budget page to add one.")
    else:
        rows = []
        for _, b in budgets.iterrows():
            if b["budget_type"] == "expenditure":
                actual = exp_df[exp_df["category"] == b["category"]]["amount"].sum() if not exp_df.empty else 0
            else:
                sales_cat = other_revenue_total if b["category"].lower() == "sales" else 0
                actual_rev = rev_df[rev_df["category"] == b["category"]]["amount"].sum() if not rev_df.empty else 0
                actual = actual_rev + (sales_total if b["category"].lower() == "sales" else 0)
            rows.append({
                "Type": b["budget_type"].title(),
                "Category": b["category"],
                "Budgeted": b["budgeted_amount"],
                "Actual": actual,
                "Variance": b["budgeted_amount"] - actual if b["budget_type"] == "expenditure" else actual - b["budgeted_amount"],
            })
        bva_df = pd.DataFrame(rows)
        st.dataframe(bva_df.style.format({"Budgeted": "₦{:,.2f}", "Actual": "₦{:,.2f}", "Variance": "₦{:,.2f}"}),
                     use_container_width=True, hide_index=True)

    # ---- Loans & Investments quick view ----
    st.divider()
    col_l, col_i = st.columns(2)
    with col_l:
        st.subheader("Loan Balances")
        loans = da.get_loans(user_id)
        if not loans.empty:
            loans["balance"] = loans.apply(lambda r: da.get_loan_balance(r["id"], r["principal_amount"]), axis=1)
            st.dataframe(
                loans[["lender", "loan_type", "principal_amount", "balance", "status"]].rename(
                    columns={"lender": "Lender", "loan_type": "Type", "principal_amount": "Principal",
                             "balance": "Balance", "status": "Status"}),
                use_container_width=True, hide_index=True)
        else:
            st.caption("No loans recorded yet.")

    with col_i:
        st.subheader("Investments")
        invs = da.get_investments(user_id)
        if not invs.empty:
            st.dataframe(
                invs[["name", "inv_type", "amount", "current_value", "status"]].rename(
                    columns={"name": "Name", "inv_type": "Type", "amount": "Invested",
                             "current_value": "Current Value", "status": "Status"}),
                use_container_width=True, hide_index=True)
        else:
            st.caption("No investments recorded yet.")
