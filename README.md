# Finance Manager

A Streamlit web app to track **expenditure, revenue, profit/loss, budgets, investments, loans, and sales** (with a product catalog) for one person or a whole team — backed by a local SQLite database.

## Features

- **Sales** — build a sale from multiple products (or custom items), auto-deducts stock, computes totals
- **Products** — catalog with selling price, cost price, and stock quantity
- **Expenditure** — categorized spending log
- **Revenue** — non-sales income (services, interest, grants, etc.)
- **Budget** — set monthly targets per category, compared automatically against actuals on the Dashboard
- **Investments** — track amount invested, current value, and gain/loss
- **Loans** — both money you've borrowed and money you've lent, with repayment tracking and running balances
- **Dashboard** — revenue vs. expenditure trend, profit/loss, expenditure breakdown, top products, budget vs. actual, loan balances, and investment portfolio — all in one view
- **Accounts** — supports a single user, or multiple people each with their own login; every record is scoped to the logged-in account so nobody sees anyone else's data

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   streamlit run app.py
   ```
3. Open the URL Streamlit prints (usually `http://localhost:8501`).
4. On first run, go to the **Create Account** tab and register. If it's just you, create one account and always log in with it. If you have teammates, each person registers their own account.

The database file `finance_system.db` is created automatically in the project folder the first time you run the app. It's a plain SQLite file — you can back it up by copying it, or open it with any SQLite browser (e.g. DB Browser for SQLite) if you want to inspect the raw data.

## Project structure

```
finance_system/
├── app.py                # Entry point: login/registration + page navigation
├── database.py            # SQLite schema and connection helper
├── auth.py                 # Registration / login (bcrypt password hashing)
├── data_access.py       # All CRUD/query functions used by pages
├── requirements.txt
└── modules/
    ├── dashboard.py       # Overview: P&L, charts, budget vs actual
    ├── products.py        # Product catalog + stock adjustments
    ├── sales.py             # Multi-item sales entry + history
    ├── expenditure.py    # Expense logging
    ├── revenue.py         # Non-sales income logging
    ├── budget.py           # Monthly budget targets
    ├── investments.py   # Investment portfolio tracking
    └── loans.py             # Loans borrowed/lent + repayments
```

## Notes

- Currency is displayed in Naira (₦) throughout, matching typical Nigerian business use — easy to change if needed (search for `₦` across the `modules/` folder).
- Net profit on the Dashboard = Total Revenue (sales + other income) − Total Expenditure − Cost of Goods Sold (based on each product's cost price at time of sale).
- To reset all data, simply stop the app and delete `finance_system.db` — it will be recreated empty on the next run.

## Extending it

Ideas if you want to build on this later:
- Paystack/bank API integration to auto-import transactions
- PDF/Excel export of reports (the `pdf`/`xlsx`/`docx` skills can help generate these)
- Multi-currency support
- Recurring expenditure/revenue templates
- Role-based permissions (e.g. viewer vs. editor) if you add more teammates
