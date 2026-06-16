import re
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WalletAI",
    page_icon="💰",
    layout="wide",
)

# ============================================================
# THEME
# ============================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "transactions" not in st.session_state:
    categories = [
        "Groceries",
        "Dining",
        "Coffee",
        "Shopping",
        "Transport",
        "Utilities",
        "Entertainment",
    ]

    rows = []

    for i in range(180):
        rows.append(
            {
                "date": datetime.now() - timedelta(days=i),
                "category": random.choice(categories),
                "amount": round(random.uniform(3, 120), 2),
                "type": "expense",
            }
        )

    st.session_state.transactions = pd.DataFrame(rows)

if "goals" not in st.session_state:
    st.session_state.goals = [
        {"goal": "Emergency Fund", "progress": 78},
        {"goal": "Vacation", "progress": 52},
        {"goal": "New Laptop", "progress": 30},
    ]

theme_toggle = st.sidebar.toggle(
    "🌗 Dark Mode",
    value=st.session_state.dark_mode
)

st.session_state.dark_mode = theme_toggle

BG = "#0E1117" if st.session_state.dark_mode else "#FFFFFF"
CARD = "#161B22" if st.session_state.dark_mode else "#F8F9FA"
TEXT = "#FAFAFA" if st.session_state.dark_mode else "#111111"

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color:{BG};
    }}

    .wallet-card {{
        padding:18px;
        border-radius:18px;
        background:{CARD};
        border:1px solid rgba(255,255,255,0.08);
        margin-bottom:10px;
    }}

    .metric-title {{
        color:gray;
        font-size:14px;
    }}

    .metric-value {{
        font-size:32px;
        font-weight:700;
    }}

    .ai-box {{
        padding:15px;
        border-radius:15px;
        background:{CARD};
        margin-bottom:10px;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💰 WalletAI")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "💸 Expenses",
        "🎯 Goals",
        "📈 Investments",
    ],
)

# ============================================================
# DATA HELPERS
# ============================================================

def generate_cashflow_data():

    dates = pd.date_range(end=datetime.now(), periods=12, freq="ME")

    income = np.random.randint(5000, 6500, len(dates))
    expenses = np.random.randint(1200, 2600, len(dates))

    return pd.DataFrame(
        {
            "Month": dates,
            "Income": income,
            "Expenses": expenses,
        }
    )


def networth_data():

    return pd.DataFrame(
        {
            "Asset": [
                "Cash",
                "Investments",
                "Emergency Fund",
                "Crypto",
            ],
            "Value": [
                15000,
                25000,
                7000,
                3000,
            ],
        }
    )


def top_expenses_data():

    return pd.DataFrame(
        {
            "Category": [
                "Shopping",
                "Dining",
                "Groceries",
                "Transport",
                "Coffee",
            ],
            "Amount": [
                890,
                620,
                510,
                340,
                160,
            ],
        }
    )


# ============================================================
# NLP EXPENSE PARSER
# ============================================================

def parse_expense_text(text):

    matches = re.findall(
        r"([A-Za-z ]+?)\s*\$?(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    parsed = []

    for label, amount in matches:

        category = label.strip().title()

        if category:
            parsed.append(
                {
                    "date": datetime.now(),
                    "category": category,
                    "amount": float(amount),
                    "type": "expense",
                }
            )

    return parsed


# ============================================================
# AI ASSISTANT
# ============================================================

def assistant_response(prompt):

    lower = prompt.lower()

    if "coffee" in lower and "spend" in lower:
        return (
            "☕ You spent approximately **$164** "
            "on Coffee during the past 30 days."
        )

    if "grocery" in lower and "dining" in lower:

        compare_df = pd.DataFrame(
            {
                "Month": [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                ],
                "Groceries": [
                    420,
                    480,
                    460,
                    500,
                    520,
                    540,
                ],
                "Dining": [
                    650,
                    620,
                    710,
                    670,
                    740,
                    760,
                ],
            }
        )

        return {
            "message":
                "📊 Grocery vs Dining comparison "
                "for the past 6 months.",
            "data": compare_df,
        }

    if "compare" in lower:
        sample = pd.DataFrame(
            {
                "Category": ["Groceries", "Dining"],
                "Amount": [540, 760],
            }
        )

        return {
            "message":
                "Comparison generated.",
            "data": sample,
        }

    return (
        "🤖 Based on your spending patterns, "
        "you remain on track to hit your savings goal "
        "this month."
    )


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "📊 Dashboard":

    st.title("💰 WalletAI Dashboard")

    income = 5500
    expenses = 1879
    balance = 3620

    # --------------------------------------------------------
    # TOP METRICS
    # --------------------------------------------------------

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            "💵 Income",
            f"S$ {income:,.0f}",
        )

    with m2:
        st.metric(
            "💸 Expenses",
            f"S$ {expenses:,.0f}",
        )

    with m3:
        st.metric(
            "🏦 Balance",
            f"S$ {balance:,.0f}",
        )

    st.divider()

    left, right = st.columns([2.3, 1])

    # --------------------------------------------------------
    # LEFT ANALYTICS
    # --------------------------------------------------------

    with left:

        cashflow_df = generate_cashflow_data()

        st.subheader("📈 Cashflow Trend")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=cashflow_df["Month"],
                y=cashflow_df["Income"],
                mode="lines",
                name="Income",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=cashflow_df["Month"],
                y=cashflow_df["Expenses"],
                mode="lines",
                name="Expenses",
            )
        )

        fig.update_layout(height=350)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        c1, c2 = st.columns(2)

        with c1:

            st.subheader("🥧 Net Worth")

            net_df = networth_data()

            pie = px.pie(
                net_df,
                values="Value",
                names="Asset",
                hole=0.6,
            )

            st.plotly_chart(
                pie,
                use_container_width=True
            )

        with c2:

            st.subheader("🔥 Top Expenses")

            exp_df = top_expenses_data()

            bar = px.bar(
                exp_df,
                x="Amount",
                y="Category",
                orientation="h",
            )

            st.plotly_chart(
                bar,
                use_container_width=True
            )

    # --------------------------------------------------------
    # AI INSIGHTS PANEL
    # --------------------------------------------------------

    with right:

        st.subheader("🧠 AI Insights")

        st.error("🔴 Shopping Budget Exceeded")

        st.warning("🟡 Unusual Shopping Spending")

        st.success("🟢 On Track for Savings Goal")

        st.info(
            "💡 Dining expenses increased 14% "
            "compared to last month."
        )

    st.divider()

    # --------------------------------------------------------
    # AI ASSISTANT CHAT
    # --------------------------------------------------------

    st.subheader("🤖 WalletAI Assistant")

    chat_container = st.container(height=450)

    with chat_container:

        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):

                st.write(message["content"])

                if "chart" in message:
                    st.bar_chart(message["chart"])

    user_prompt = st.chat_input(
        "Ask WalletAI anything..."
    )

    if user_prompt:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        response = assistant_response(user_prompt)

        if isinstance(response, dict):

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": response["message"],
                    "chart": response["data"],
                }
            )

        else:

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

        st.rerun()

# ============================================================
# EXPENSES PAGE
# ============================================================

elif page == "💸 Expenses":

    st.title("💸 Expense Logger")

    st.markdown(
        """
        Example:

        - Had coffee $5 and lunch $12 today
        - Starbucks coffee $6
        - Dinner $22 and taxi $15
        """
    )

    text = st.text_area(
        "Enter expense in natural language"
    )

    if st.button("➕ Add Expense"):

        parsed = parse_expense_text(text)

        if parsed:

            df_new = pd.DataFrame(parsed)

            st.session_state.transactions = pd.concat(
                [
                    st.session_state.transactions,
                    df_new,
                ],
                ignore_index=True,
            )

            st.success(
                f"Added {len(parsed)} expense(s)"
            )

        else:
            st.warning(
                "Could not detect expenses."
            )

    st.subheader("📋 Transaction History")

    st.dataframe(
        st.session_state.transactions.sort_values(
            "date",
            ascending=False,
        ),
        use_container_width=True,
        height=500,
    )

# ============================================================
# GOALS PAGE
# ============================================================

elif page == "🎯 Goals":

    st.title("🎯 Financial Goals")

    for goal in st.session_state.goals:

        st.markdown(
            f"### {goal['goal']}"
        )

        st.progress(goal["progress"] / 100)

        st.caption(
            f"{goal['progress']}% completed"
        )

# ============================================================
# INVESTMENTS PAGE
# ============================================================

elif page == "📈 Investments":

    st.title("📈 Investment Portfolio")

    portfolio = pd.DataFrame(
        {
            "Asset": [
                "ETF",
                "Stocks",
                "Crypto",
                "Cash",
            ],
            "Value": [
                18000,
                12000,
                3000,
                15000,
            ],
        }
    )

    fig = px.treemap(
        portfolio,
        path=["Asset"],
        values="Value",
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        portfolio,
        use_container_width=True
    )
