import streamlit as st
import data_access as da


def render(user_id):
    st.header("📦 Products")

    with st.expander("➕ Add New Product", expanded=False):
        with st.form("add_product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Product Name*")
                sku = st.text_input("SKU / Code")
                category = st.text_input("Category")
            with c2:
                unit_price = st.number_input("Selling Price (₦)*", min_value=0.0, step=100.0)
                cost_price = st.number_input("Cost Price (₦)", min_value=0.0, step=100.0)
                stock_qty = st.number_input("Initial Stock Qty", min_value=0.0, step=1.0)

            submitted = st.form_submit_button("Add Product")
            if submitted:
                if not name or unit_price <= 0:
                    st.error("Product name and a selling price greater than 0 are required.")
                else:
                    da.add_product(user_id, name, sku, category, unit_price, cost_price, stock_qty)
                    st.success(f"Added '{name}'.")
                    st.rerun()

    st.subheader("Product Catalog")
    products = da.get_products(user_id)
    if products.empty:
        st.info("No products yet. Add your first product above.")
        return

    display_df = products[["name", "sku", "category", "unit_price", "cost_price", "stock_qty"]].rename(
        columns={"name": "Name", "sku": "SKU", "category": "Category",
                 "unit_price": "Selling Price", "cost_price": "Cost Price", "stock_qty": "Stock"}
    )
    st.dataframe(display_df.style.format({"Selling Price": "₦{:,.2f}", "Cost Price": "₦{:,.2f}"}),
                 use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Adjust Stock / Deactivate")
    prod_options = {f"{r['name']} (stock: {r['stock_qty']})": r["id"] for _, r in products.iterrows()}
    selected_label = st.selectbox("Select product", list(prod_options.keys()))
    selected_id = prod_options[selected_label]

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        delta = st.number_input("Stock adjustment (+ to add, - to remove)", value=0.0, step=1.0)
    with c2:
        if st.button("Apply Adjustment"):
            da.update_stock(selected_id, delta)
            st.success("Stock updated.")
            st.rerun()
    with c3:
        if st.button("Deactivate Product", type="secondary"):
            da.deactivate_product(selected_id)
            st.success("Product deactivated.")
            st.rerun()
