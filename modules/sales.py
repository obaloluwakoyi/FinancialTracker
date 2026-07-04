import streamlit as st
import pandas as pd
from datetime import date
import data_access as da


def render(user_id):
    st.header("🛒 Sales")

    products = da.get_products(user_id)

    st.subheader("Record a New Sale")
    if "cart" not in st.session_state:
        st.session_state.cart = []

    with st.form("add_line_item", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            if not products.empty:
                prod_choice = st.selectbox(
                    "Product", ["-- custom item --"] + products["name"].tolist()
                )
            else:
                prod_choice = "-- custom item --"
                st.caption("No products in catalog yet — you can still enter a custom item, or add products on the Products page.")
        with c2:
            qty = st.number_input("Quantity", min_value=0.0, value=1.0, step=1.0)
        with c3:
            custom_price = st.number_input("Unit Price (₦) — leave 0 to use catalog price", min_value=0.0, step=100.0)

        add_item = st.form_submit_button("➕ Add to Sale")
        if add_item:
            if prod_choice != "-- custom item --":
                prow = products[products["name"] == prod_choice].iloc[0]
                price = custom_price if custom_price > 0 else prow["unit_price"]
                st.session_state.cart.append({
                    "product_id": int(prow["id"]),
                    "product_name": prow["name"],
                    "quantity": qty,
                    "unit_price": price,
                    "cost_price": prow["cost_price"],
                })
            else:
                if custom_price <= 0:
                    st.error("Enter a unit price for the custom item.")
                else:
                    st.session_state.cart.append({
                        "product_id": None,
                        "product_name": "Custom item",
                        "quantity": qty,
                        "unit_price": custom_price,
                        "cost_price": 0,
                    })

    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df["Subtotal"] = cart_df["quantity"] * cart_df["unit_price"]
        st.dataframe(
            cart_df[["product_name", "quantity", "unit_price", "Subtotal"]].rename(
                columns={"product_name": "Product", "quantity": "Qty", "unit_price": "Unit Price"}),
            use_container_width=True, hide_index=True
        )
        st.write(f"**Sale Total: ₦{cart_df['Subtotal'].sum():,.2f}**")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear items"):
                st.session_state.cart = []
                st.rerun()

        with st.form("finalize_sale"):
            sale_date = st.date_input("Sale Date", value=date.today())
            customer_name = st.text_input("Customer Name (optional)")
            payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Card", "POS", "Paystack", "Other"])
            notes = st.text_area("Notes (optional)")
            finalize = st.form_submit_button("✅ Complete Sale")
            if finalize:
                da.add_sale(user_id, str(sale_date), customer_name, payment_method, notes, st.session_state.cart)
                st.session_state.cart = []
                st.success("Sale recorded successfully.")
                st.rerun()
    else:
        st.caption("Add one or more items above to build a sale, then complete it.")

    st.divider()
    st.subheader("Sales History")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("From", value=date.today().replace(day=1), key="sales_start")
    with c2:
        end_date = st.date_input("To", value=date.today(), key="sales_end")

    sales_df = da.get_sales(user_id, str(start_date), str(end_date))
    if sales_df.empty:
        st.info("No sales recorded in this period.")
        return

    st.dataframe(
        sales_df[["sale_date", "customer_name", "payment_method", "total_amount", "notes"]].rename(
            columns={"sale_date": "Date", "customer_name": "Customer", "payment_method": "Payment",
                     "total_amount": "Total", "notes": "Notes"}
        ).style.format({"Total": "₦{:,.2f}"}),
        use_container_width=True, hide_index=True
    )

    with st.expander("View line items for a specific sale"):
        sale_ids = sales_df["id"].tolist()
        if sale_ids:
            chosen = st.selectbox("Select Sale ID", sale_ids)
            items = da.get_sale_items(chosen)
            if not items.empty:
                st.dataframe(
                    items[["product_name", "quantity", "unit_price", "subtotal"]].rename(
                        columns={"product_name": "Product", "quantity": "Qty",
                                 "unit_price": "Unit Price", "subtotal": "Subtotal"}
                    ).style.format({"Unit Price": "₦{:,.2f}", "Subtotal": "₦{:,.2f}"}),
                    use_container_width=True, hide_index=True
                )
