import streamlit as st
from database import init_db
from auth import register_user, authenticate_user
from modules import dashboard, products, sales, expenditure, revenue, budget, operations, loans, history

st.set_page_config(page_title="Finance Manager", page_icon="💼", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --panel: #0f172a;
        --panel-2: #111c31;
        --text: #f8fafc;
        --muted: #94a3b8;
        --accent: #14b8a6;
        --accent-2: #38bdf8;
        --border: rgba(148, 163, 184, 0.25);
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, var(--bg) 0%, #0f172a 100%);
        color: var(--text);
    }
    [data-testid="stSidebar"] {
        background: rgba(7, 17, 31, 0.96);
        border-right: 1px solid var(--border);
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.18), rgba(56, 189, 248, 0.12));
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(2, 8, 23, 0.25);
    }
    .hero-card h1 {
        font-size: 2rem;
        margin-bottom: 0.25rem;
        color: white;
    }
    .hero-card p {
        color: var(--muted);
        font-size: 1rem;
        margin-bottom: 0;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(20, 184, 166, 0.2);
        color: #99f6e4;
        border: 1px solid rgba(20, 184, 166, 0.35);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
        letter-spacing: 0.03em;
    }
    .page-title {
        padding: 0.3rem 0 0.8rem 0;
    }
    .page-title h1 {
        margin-bottom: 0.1rem;
    }
    .page-title p {
        color: var(--muted);
        margin-top: 0;
    }
    div[data-testid="stBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
        gap: 0.6rem;
    }
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.8rem 1rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.15);
    }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        border: none;
        box-shadow: 0 8px 20px rgba(20, 184, 166, 0.25);
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: var(--panel-2);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 10px;
    }
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    /* Headings, captions, and text stay legible on the dark background */
    h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }
    p, span, label, .stMarkdown, .stCaption { color: var(--text); }
    [data-testid="stCaptionContainer"] { color: var(--muted) !important; }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: var(--panel-2);
        border-radius: 10px 10px 0 0;
        color: var(--muted);
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(20, 184, 166, 0.18) !important;
        color: #99f6e4 !important;
    }
    /* Expander */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {
        background: var(--panel-2);
        border-radius: 10px;
        color: var(--text) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()

# --------------------------------------------------------------------------
# AUTH GATE
# --------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">Finance Manager</div>
            <h1>Stay on top of your finances with clarity</h1>
            <p>Monitor revenue, expenses, profit, budgets, loans, operations, and sales from a single clean workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Sign in to continue or create your account to get started.")

    tab_login, tab_register = st.tabs(["Log In", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            if submitted:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_register:
        st.caption("Create one account if you're the only user, or one account per teammate — "
                   "each account only ever sees its own records.")
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_full_name = st.text_input("Full name (optional)")
            new_password = st.text_input("Choose a password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted_r = st.form_submit_button("Create Account")
            if submitted_r:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(new_username, new_password, new_full_name)
                    if success:
                        st.success(message + " Switch to the Log In tab.")
                    else:
                        st.error(message)

    st.stop()

# --------------------------------------------------------------------------
# MAIN APP (authenticated)
# --------------------------------------------------------------------------
user = st.session_state.user

with st.sidebar:
    st.markdown(
        f"""
        <div class="hero-card" style="padding: 1rem; margin-bottom: 0.75rem;">
            <div class="hero-badge">Finance Manager</div>
            <h3 style="margin: 0.2rem 0; font-size: 1.1rem;">💼 {user['full_name'] or user['username']}</h3>
            <p style="margin: 0; color: var(--muted);">Manage your business finances in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        ["Dashboard", "Sales", "Products", "Expenditure", "Revenue", "Budget", "Operations", "Loans", "History"],
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("Log Out"):
        st.session_state.user = None
        st.rerun()

PAGES = {
    "Dashboard": dashboard.render,
    "Sales": sales.render,
    "Products": products.render,
    "Expenditure": expenditure.render,
    "Revenue": revenue.render,
    "Budget": budget.render,
    "Operations": operations.render,
    "Loans": loans.render,
    "History": history.render,
}

PAGES[page](user["id"])
