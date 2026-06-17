import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# ==============================================================================
# CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="WalletAI — Premium Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium UI enhancements via CSS injections
st.markdown("""
    <style>
    /* Premium font adjustments and subtle grid padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Sleek container styles mimicking modern card layouts */
    div[data-testid="stVerticalBlock"] > div:has(div.metric-card) {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e9ecef;
    }
    /* AI Assistant floating UI custom styling hints */
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA SIMULATION LAYER & PERSISTENT SESSION STATE
# ==============================================================================
def initialize_session_state():
    # Simulated Historical Transaction Logs
    if 'transactions' not in st.session_state:
        base_date = datetime.now()
        st.session_state.transactions = pd.DataFrame([
            {"Date": (base_date - timedelta(days=5)).strftime("%Y-%m-%d"), "Description": "Starbucks Coffee", "Category": "Food & Dining", "Amount": 8.50, "Type": "Expense"},
            {"Date": (base_date - timedelta(days=4)).strftime("%Y-%m-%d"), "Description": "Monthly Salary", "Category": "Salary", "Amount": 5500.00, "Type": "Income"},
            {"Date": (base_date - timedelta(days=3)).strftime("%Y-%m-%d"), "Description": "Grocery Supermarket", "Category": "Groceries", "Amount": 124.90, "Type": "Expense"},
            {"Date": (base_date - timedelta(days=2)).strftime("%Y-%m-%d"), "Description": "Uniqlo Clothing Shopping", "Category": "Shopping", "Amount": 1022.90, "Type": "Expense"},
            {"Date": (base_date - timedelta(days=1)).strftime("%Y-%m-%d"), "Description": "Uber Ride", "Category": "Transport", "Amount": 24.50, "Type": "Expense"},
            {"Date": base_date.strftime("%Y-%m-%d"), "Description": "Sushi Dinner", "Category": "Food & Dining", "Amount": 75.00, "Type": "Expense"}
        ])

    # Simulated Financial Goals
    if 'goals' not in st.session_state:
        st.session_state.goals = [
            {"Target": "Save for Car Downpayment", "Current": 41620, "Goal": 60000, "Icon": "🚗"},
            {"Target": "Taiwan Trip Fund", "Current": 1800, "Goal": 2000, "Icon": "✈️"}
        ]
# Insert these inside your initialize_session_state() block
if 'base_monthly_income' not in st.session_state:
    st.session_state.base_monthly_income = 5500.00

if 'monthly_savings_goal' not in st.session_state:
    st.session_state.monthly_savings_goal = 2000.00
    # Chat Log History Management
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello Jayden! I'm your **WalletAI** financial assistant powered by Gemini. Ask me anything about your current spending trends, budgets, or ask me to compare categories!"}
        ]


    # Dark Mode Tracker Simulation state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

initialize_session_state()


# ==============================================================================
# NATURAL LANGUAGE PROCESSING BACKEND (MOCK ENGINE)
# ==============================================================================
def parse_natural_language_expense(text: str):
    """
    Parses natural language strings like 'Had coffee $5 and lunch $12 today'
    into structured categorical transactional list objects.
    """
    extracted_items = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Simple regex searching for descriptors and localized monetary currency tags
    matches = re.findall(r'([A-Za-z\s]+)\s?\$?\s?(\d+(?:\.\d{2})?)', text)
    
    if not matches:
        # Fallback heuristic if format is unique
        return [{"Date": current_date, "Description": text, "Category": "Uncategorized", "Amount": 20.00, "Type": "Expense"}]
        
    for desc, amt in matches:
        clean_desc = desc.strip().lower()
        # Clean linking words out
        for word in ['had', 'and', 'bought', 'for', 'today']:
            clean_desc = clean_desc.replace(word, "").strip()
            
        # Predictive baseline category router
        category = "Other"
        if any(k in clean_desc for k in ['coffee', 'lunch', 'dinner', 'food', 'sushi', 'cafe']):
            category = "Food & Dining"
        elif any(k in clean_desc for k in ['groceries', 'mart', 'supermarket', 'milk']):
            category = "Groceries"
        elif any(k in clean_desc for k in ['shirt', 'cloth', 'shopping', 'shoes', 'mall']):
            category = "Shopping"
        elif any(k in clean_desc for k in ['uber', 'grab', 'taxi', 'mrt', 'bus']):
            category = "Transport"
            
        extracted_items.append({
            "Date": current_date,
            "Description": desc.strip().capitalize(),
            "Category": category,
            "Amount": float(amt),
            "Type": "Expense"
        })
    return extracted_items


# ==============================================================================
# SIDEBAR NAVIGATION & THEME CONTROLLER
# ==============================================================================
with st.sidebar:
    st.title("💳 WalletAI")
    st.caption("Intelligence-Driven Wealth Management")
    st.markdown("---")
    
    # Navigation Matrix
    navigation_pane = st.radio(
        "Navigation Menu",
        options=["📊 Dashboard", "💸 Expenses", "🎯 Goals", "📈 Investments"],
        index=0
    )
    
    st.markdown("---")
    # Quick Simulation Toggle for light/dark properties
    st.subheader("Preferences")
    toggle_mode = st.toggle("🌙 Dark Mode Aesthetic Theme", value=st.session_state.dark_mode)
    if toggle_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = toggle_mode
        st.rerun()

    st.markdown("---")
    st.info("💡 **Tip:** Go to the **Expenses** tab to test parsing transactional data from conversational entries.")


# ==============================================================================
# ROUTED APPLICATION PAGES
# ==============================================================================

# 📊 VIEW LAYER: DASHBOARD
if navigation_pane == "📊 Dashboard":
    st.title("Financial Dashboard")
    st.markdown(f"Welcome back, **Jayden** — here is your financial snapshot for **{datetime.now().strftime('%B %Y')}**.")
    
  
# Income dynamically reflects your base settings + any manually logged side-income
total_income = st.session_state.base_monthly_income + df_tx[df_tx['Type'] == 'Income']['Amount'].sum()
total_expenses = df_tx[df_tx['Type'] == 'Expense']['Amount'].sum()
net_balance = total_income - total_expenses
    
    # Top Row Metrics Layout
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="Income", value=f"S$ {total_income:,.2f}", delta="+3.5% vs last month")
    with m_col2:
        st.metric(label="Expenses", value=f"S$ {total_expenses:,.2f}", delta=f"-S$ {total_expenses:,.2f}", delta_color="inverse")
    with m_col3:
        st.metric(label="Balance", value=f"S$ {net_balance:,.2f}", delta="+12.4% net positive change")
        
    st.markdown("---")
    
    # Core Data Visualization Grid Layout
    left_grid, right_grid = st.columns([2, 1])
    
    with left_grid:
        st.subheader("Cashflow Analytics Trend")
        # Creating simple line trend matrix
        dates = pd.date_range(end=datetime.now(), periods=6).strftime("%Y-%m-%d").tolist()
        cashflow_mock = pd.DataFrame({
            'Date': dates,
            'Income': [5500, 5500, 5500, 5500, 5500, 5500],
            'Expenses': [1420, 1650, 1200, 1980, 1540, float(total_expenses)]
        })
        fig_cf = px.line(cashflow_mock, x='Date', y=['Income', 'Expenses'], 
                         color_discrete_sequence=['#2ecc71', '#e74c3c'], template="plotly_white")
        fig_cf.update_layout(height=320, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig_cf, use_container_width=True)
        
        col_bl, col_br = st.columns(2)
        with col_bl:
            st.subheader("Net Worth Breakdown")
            nw_data = pd.DataFrame({
                'Asset Class': ['Investments', 'Wallets', 'Cash Reserves', 'E-Wallet Assets'],
                'Value': [76707, 5945, 105600, 3200]
            })
            fig_nw = px.pie(nw_data, values='Value', names='Asset Class', hole=0.5,
                            color_discrete_sequence=px.colors.sequential.YlGnBu_r)
            fig_nw.update_layout(height=260, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_nw, use_container_width=True)
            
        with col_br:
            st.subheader("Top Expense Categories")
            expense_only = df_tx[df_tx['Type'] == 'Expense']
            if not expense_only.empty:
                cat_summary = expense_only.groupby('Category')['Amount'].sum().reset_index()
                fig_cat = px.bar(cat_summary, x='Amount', y='Category', orientation='h',
                                 color='Amount', color_continuous_scale='Reds')
                fig_cat.update_layout(height=260, coloraxis_showscale=False, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No recorded expenses to visualize.")

        # Bottom Row: Recent Transaction Tracking Log
        st.subheader("Recent Transactions History Log")
        st.dataframe(df_tx.sort_values(by="Date", ascending=False), use_container_width=True)

    with right_grid:
        st.subheader("✨ AI Engine Insights")
        
        # Simulated dynamic warning conditions driven by state logs
        if total_expenses > 1500:
            st.error("""
                **🔴 Shopping Budget Exceeded** Your current monthly expenditure on retail items has surpassed your targeted safety boundary threshold of **S$ 1,000.00**.
            """)
        else:
            st.success("**🟢 Shopping Budget Stable**\nYour spending tracks perfectly below margins.")
            
        st.warning("""
            **🟡 Unusual Velocity Check** An anomalous recurring entertainment charge spike was identified between 2 AM - 4 AM earlier this week. Consider reviewing automated application tracking permissions.
        """)
        
        st.info("""
            **🟢 On Track for Financial Milestone** At your current localized generation speed of cash velocity accumulation, your targeted milestone **'Save for Car Downpayment'** will complete 1.4 months early.
        """)
        
        # Interactive Chat Assistant widget embedded inside container layout
        st.markdown("---")
        st.subheader("🤖 Live Assistant Interface")
        
        chat_container = st.container(height=350)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if "chart" in msg:
                        st.plotly_chart(msg["chart"], use_container_width=True)
                        
        if user_query := st.chat_input("Ask WalletAI anything..."):
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Smart Mock Engine Query Route Handler
            norm_query = user_query.lower()
            response_payload = {}
            
            if "coffee" in norm_query:
                coffee_sum = df_tx[df_tx['Description'].str.contains('Coffee', case=False, na=False)]['Amount'].sum()
                response_payload["content"] = f"Checking records... You've spent a total of **S$ {coffee_sum:.2f}** on coffee items listed within the database log sequence."
            elif "compare" in norm_query or "grocery vs dining" in norm_query:
                response_payload["content"] = "Here is the categorical contrast distribution matrix across the requested 6-month tracking timeline:"
                compare_df = pd.DataFrame({
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'Groceries': [120, 140, 90, 110, 130, 124],
                    'Food & Dining': [210, 185, 300, 240, 190, 835]
                })
                fig_comp = px.bar(compare_df, x='Month', y=['Groceries', 'Food & Dining'], barmode='group',
                                  color_discrete_sequence=['#3498db', '#e67e22'])
                fig_comp.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
                response_payload["chart"] = fig_comp
            else:
                response_payload["content"] = "Understood. I will run that vector pattern optimization query across your database timeline and provide feedback metrics shortly."
                
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(response_payload["content"])
                    if "chart" in response_payload:
                        st.plotly_chart(response_payload["chart"], use_container_width=True)
                        
            st.session_state.chat_history.append({"role": "assistant", **response_payload})


# 💸 VIEW LAYER: EXPENSES MANIPULATION
elif navigation_pane == "💸 Expenses":
    st.title("Expense Management & Intelligent Logging")
    
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("Natural Language AI Log Engine")
        st.write("Type naturally to instantly add structured database entries.")
        
        sample_input = "Had coffee $5 and lunch $12 today"
        user_text_expense = st.text_input(
            "Describe purchase statement entry:",
            placeholder=f"e.g., {sample_input}"
        )
        
        if st.button("✨ Parse and Commit Transaction", type="primary"):
            if user_text_expense:
                parsed_records = parse_natural_language_expense(user_text_expense)
                for record in parsed_records:
                    new_row = pd.DataFrame([record])
                    st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                st.success(f"Successfully processed {len(parsed_records)} data rows into session storage ledger!")
                st.balloons()
            else:
                st.warning("Please type a descriptive tracking entry string sentence first.")
                
    with col_r:
        st.subheader("Current Core Transaction Registry")
        st.dataframe(st.session_state.transactions, use_container_width=True)


# 🎯 VIEW LAYER: GOALS TRACKING
elif navigation_pane == "🎯 Goals":
    st.title("Financial Goals Management Matrix")
    
    st.write("Keep track of your targets and automatic structural progress accumulation metrics.")
    
    for g in st.session_state.goals:
        pct = min(g["Current"] / g["Goal"], 1.0)
        st.markdown(f"### {g['Icon']} {g['Target']}")
        st.progress(pct)
        st.markdown(f"**Progress:** {pct*100:.1f}% (`S$ {g['Current']:,}` of `S$ {g['Goal']:,}` targets achieved)")
        st.markdown("---")


# 📈 VIEW LAYER: INVESTMENTS PORTFOLIO
elif navigation_pane == "📈 Investments":
    st.title("Asset & Investment Tracking Desk")
    
    inv_col1, inv_col2 = st.columns([2, 1])
    
    with inv_col1:
        st.subheader("Aggregated Performance Metric Distribution")
        timeline_idx = pd.date_range(end=datetime.now(), periods=12, freq='ME')
        perf_mock = pd.DataFrame({
            'Timeline': timeline_idx,
            'Portfolio Value (S$)': [50000, 52000, 51000, 55000, 58000, 62000, 60000, 65000, 70000, 72000, 74000, 76000]
        })
        fig_perf = px.area(perf_mock, x='Timeline', y='Portfolio Value (S$)', color_discrete_sequence=['#16a085'])
        st.plotly_chart(fig_perf, use_container_width=True)
        
    with inv_col2:
        st.subheader("Current Target Holdings Allocation")
        holdings = pd.DataFrame({
            'Ticker Asset': ['BTC-USD', 'NVDA', 'TSLA', 'SPY ETF'],
            'Weight Mapping (%)': [40, 30, 15, 15]
        })
        fig_holdings = px.pie(holdings, values='Weight Mapping (%)', names='Ticker Asset', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_holdings, use_container_width=True)
