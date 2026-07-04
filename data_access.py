"""
data_access.py
All CRUD / query functions used by the Streamlit pages, scoped per user_id
so that in multi-user mode each account only ever sees its own records.
"""

import pandas as pd
from database import get_connection


def _df(query, params=()):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def _execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# ---------------------------------------------------------------- PRODUCTS
def add_product(user_id, name, sku, category, unit_price, cost_price, stock_qty):
    return _execute(
        """INSERT INTO products (user_id, name, sku, category, unit_price, cost_price, stock_qty)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, name, sku, category, unit_price, cost_price, stock_qty),
    )


def get_products(user_id, active_only=True):
    q = "SELECT * FROM products WHERE user_id = ?"
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY name"
    return _df(q, (user_id,))


def update_stock(product_id, delta_qty):
    _execute(
        "UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?",
        (delta_qty, product_id),
    )


def deactivate_product(product_id):
    _execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))


# ---------------------------------------------------------------- SALES
def add_sale(user_id, sale_date, customer_name, payment_method, notes, items):
    """items: list of dicts with product_id, product_name, quantity, unit_price, cost_price"""
    total = sum(i["quantity"] * i["unit_price"] for i in items)
    sale_id = _execute(
        """INSERT INTO sales (user_id, sale_date, customer_name, payment_method, notes, total_amount)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, sale_date, customer_name, payment_method, notes, total),
    )
    conn = get_connection()
    cur = conn.cursor()
    for i in items:
        subtotal = i["quantity"] * i["unit_price"]
        cur.execute(
            """INSERT INTO sale_items (sale_id, product_id, product_name, quantity, unit_price, cost_price, subtotal)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (sale_id, i.get("product_id"), i["product_name"], i["quantity"], i["unit_price"],
             i.get("cost_price", 0), subtotal),
        )
        if i.get("product_id"):
            cur.execute(
                "UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?",
                (i["quantity"], i["product_id"]),
            )
    conn.commit()
    conn.close()
    return sale_id


def get_sales(user_id, start_date=None, end_date=None):
    q = "SELECT * FROM sales WHERE user_id = ?"
    params = [user_id]
    if start_date:
        q += " AND sale_date >= ?"
        params.append(start_date)
    if end_date:
        q += " AND sale_date <= ?"
        params.append(end_date)
    q += " ORDER BY sale_date DESC"
    return _df(q, tuple(params))


def get_sale_items(sale_id):
    return _df("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,))


def get_sale_profit_summary(user_id, start_date=None, end_date=None):
    q = """
        SELECT si.* , s.sale_date FROM sale_items si
        JOIN sales s ON s.id = si.sale_id
        WHERE s.user_id = ?
    """
    params = [user_id]
    if start_date:
        q += " AND s.sale_date >= ?"
        params.append(start_date)
    if end_date:
        q += " AND s.sale_date <= ?"
        params.append(end_date)
    return _df(q, tuple(params))


# ---------------------------------------------------------------- EXPENDITURE
def add_expenditure(user_id, exp_date, category, description, amount, payment_method):
    return _execute(
        """INSERT INTO expenditures (user_id, exp_date, category, description, amount, payment_method)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, exp_date, category, description, amount, payment_method),
    )


def get_expenditures(user_id, start_date=None, end_date=None):
    q = "SELECT * FROM expenditures WHERE user_id = ?"
    params = [user_id]
    if start_date:
        q += " AND exp_date >= ?"
        params.append(start_date)
    if end_date:
        q += " AND exp_date <= ?"
        params.append(end_date)
    q += " ORDER BY exp_date DESC"
    return _df(q, tuple(params))


def delete_expenditure(exp_id):
    _execute("DELETE FROM expenditures WHERE id = ?", (exp_id,))


# ---------------------------------------------------------------- REVENUE (non-sales)
def add_revenue(user_id, rev_date, source, category, description, amount):
    raise ValueError("Manual revenue entries are disabled. Revenue is generated from completed sales only.")


def get_revenues(user_id, start_date=None, end_date=None):
    q = "SELECT * FROM revenues WHERE user_id = ?"
    params = [user_id]
    if start_date:
        q += " AND rev_date >= ?"
        params.append(start_date)
    if end_date:
        q += " AND rev_date <= ?"
        params.append(end_date)
    q += " ORDER BY rev_date DESC"
    return _df(q, tuple(params))


def delete_revenue(rev_id):
    _execute("DELETE FROM revenues WHERE id = ?", (rev_id,))


# ---------------------------------------------------------------- BUDGET
def upsert_budget(user_id, period, budget_type, category, amount):
    _execute(
        """INSERT INTO budgets (user_id, period, budget_type, category, budgeted_amount)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(user_id, period, budget_type, category)
           DO UPDATE SET budgeted_amount = excluded.budgeted_amount""",
        (user_id, period, budget_type, category, amount),
    )


def get_budgets(user_id, period=None):
    q = "SELECT * FROM budgets WHERE user_id = ?"
    params = [user_id]
    if period:
        q += " AND period = ?"
        params.append(period)
    q += " ORDER BY period DESC, budget_type, category"
    return _df(q, tuple(params))


def delete_budget(budget_id):
    _execute("DELETE FROM budgets WHERE id = ?", (budget_id,))


# ---------------------------------------------------------------- INVESTMENTS
def add_investment(user_id, inv_date, name, inv_type, amount, expected_return, current_value, status, notes):
    return _execute(
        """INSERT INTO investments (user_id, inv_date, name, inv_type, amount, expected_return, current_value, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, inv_date, name, inv_type, amount, expected_return, current_value, status, notes),
    )


def get_investments(user_id):
    return _df("SELECT * FROM investments WHERE user_id = ? ORDER BY inv_date DESC", (user_id,))


def update_investment_status(inv_id, status, current_value=None):
    if current_value is not None:
        _execute("UPDATE investments SET status = ?, current_value = ? WHERE id = ?", (status, current_value, inv_id))
    else:
        _execute("UPDATE investments SET status = ? WHERE id = ?", (status, inv_id))


def delete_investment(inv_id):
    _execute("DELETE FROM investments WHERE id = ?", (inv_id,))


# ---------------------------------------------------------------- LOANS
def add_loan(user_id, loan_date, lender, loan_type, principal_amount, interest_rate, term_months, purpose, notes):
    return _execute(
        """INSERT INTO loans (user_id, loan_date, lender, loan_type, principal_amount, interest_rate, term_months, purpose, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, loan_date, lender, loan_type, principal_amount, interest_rate, term_months, purpose, notes),
    )


def get_loans(user_id):
    return _df("SELECT * FROM loans WHERE user_id = ? ORDER BY loan_date DESC", (user_id,))


def add_loan_payment(loan_id, payment_date, amount, notes):
    return _execute(
        "INSERT INTO loan_payments (loan_id, payment_date, amount, notes) VALUES (?, ?, ?, ?)",
        (loan_id, payment_date, amount, notes),
    )


def get_loan_payments(loan_id):
    return _df("SELECT * FROM loan_payments WHERE loan_id = ? ORDER BY payment_date DESC", (loan_id,))


def get_loan_balance(loan_id, principal_amount):
    df = get_loan_payments(loan_id)
    paid = df["amount"].sum() if not df.empty else 0
    return principal_amount - paid


def update_loan_status(loan_id, status):
    _execute("UPDATE loans SET status = ? WHERE id = ?", (status, loan_id))


def delete_loan(loan_id):
    _execute("DELETE FROM loans WHERE id = ?", (loan_id,))
