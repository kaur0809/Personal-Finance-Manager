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
    page_title="MR.MNY // AI Wealth Desk",  # Updates the browser tab title
    page_icon="💰",                         # Updates the browser tab icon
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
# SIDEBAR NAVIGATION & PARAMETERS CONTROLLER
# ==============================================================================
with st.sidebar:
    st.title("💰 MR.MNY")
    st.caption("AI Wealth Desk // Smart Ledger")
    st.markdown("---")
    
    navigation_pane = st.radio(
        "Navigation Menu",
        options=["📊 Dashboard", "💸 Expenses", "🎯 Goals", "📈 Investments"],
        index=0
    )
    
    st.markdown("---")

    # ➕ QUICK LOG POPOVER 
    with st.popover("➕ Quick Log Expense", use_container_width=True):
        st.subheader("Fast Entry Registry")
        with st.form("quick_log_form", clear_on_submit=True):
            q_desc = st.text_input("Item Description", placeholder="e.g., Cold Brew Coffee")
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                q_amt = st.number_input("Amount (S$)", min_value=0.01, step=1.0)
            with col_q2:
                q_cat = st.selectbox("Category", ["Food & Dining", "Groceries", "Shopping", "Transport", "Other"])
                
            submit_quick = st.form_submit_button("Commit Transaction", use_container_width=True)
            if submit_quick:
                if q_desc.strip():
                    new_tx = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Description": q_desc.strip().capitalize(),
                        "Category": q_cat,
                        "Amount": float(q_amt),
                        "Type": "Expense"
                    }])
                    st.session_state.transactions = pd.concat([st.session_state.transactions, new_tx], ignore_index=True)
                    st.success("Logged instantly!")
                    st.rerun()
                else:
                    st.error("Please enter a description.")

    st.markdown("---")
    
    # ⚙️ LIVE PROFILE PARAMETERS WITH 50/30/20 BLUEPRINT CALCULATOR
    with st.expander("⚙️ Adjust Profile Parameters", expanded=True):
        st.subheader("Income Parameters")
        
        # Salary Entry Slider/Number combo
        new_income = st.number_input(
            "Base Monthly Income (S$)", 
            min_value=0.0, 
            value=float(st.session_state.base_monthly_income), 
            step=100.0,
            key="sidebar_income_input"
        )
        if new_income != st.session_state.base_monthly_income:
            st.session_state.base_monthly_income = new_income
            st.rerun()
            
        new_savings_target = st.number_input(
            "Monthly Savings Goal (S$)", 
            min_value=0.0, 
            value=float(st.session_state.monthly_savings_goal), 
            step=50.0,
            key="sidebar_savings_input"
        )
        if new_savings_target != st.session_state.monthly_savings_goal:
            st.session_state.monthly_savings_goal = new_savings_target
            st.rerun()
            
        # LIVE 50/30/20 ALLOCATION CALCULATIONS
        st.markdown("---")
        st.markdown("### 📊 50/30/20 Target Strategy")
        
        calc_income = st.session_state.base_monthly_income
        needs_alloc = calc_income * 0.50
        wants_alloc = calc_income * 0.30
        savings_alloc = calc_income * 0.20
        
        st.caption("Ideal breakdown allocation parameters:")
        st.info(f"🏠 **Needs (50%):** S$ {needs_alloc:,.2f}")
        st.warning(f"🛍️ **Wants (30%):** S$ {wants_alloc:,.2f}")
        st.success(f"📈 **Savings/Invest (20%):** S$ {savings_alloc:,.2f}")
        
        # Added safety warning if user savings target doesn't check out mathematically
        if st.session_state.monthly_savings_goal > savings_alloc:
            st.caption("⚠️ *Note: Your manual savings target is set more aggressively than the standard 20% rule cushion.*")

    st.markdown("---")
    st.subheader("Preferences")
    toggle_mode = st.toggle("🌙 Dark Mode Aesthetic Theme", value=st.session_state.dark_mode, key="sidebar_dark_mode_toggle")
    if toggle_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = toggle_mode
        st.rerun()
# ==============================================================================
# ROUTED APPLICATION PAGES
# ==============================================================================

# 📊 VIEW LAYER: DASHBOARD
if navigation_pane == "📊 Dashboard":
    st.title("Financial Dashboard")
    st.markdown(f"Welcome back, **Kaur** — here is your financial snapshot.")
    
    df_tx = st.session_state.transactions

    # NEW DYNAMIC CALCULATIONS
    total_income = st.session_state.base_monthly_income + df_tx[df_tx['Type'] == 'Income']['Amount'].sum()
    total_expenses = df_tx[df_tx['Type'] == 'Expense']['Amount'].sum()
    net_balance = total_income - total_expenses
    
    # EXACTLY 4 SPACES INFRONT OF THIS LINE:
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
    
    # ==============================================================================
    # 📊 LEFT COLUMN: CHARTS, EDITOR, & TRANSACTION LOGS
    # ==============================================================================
    with left_grid:
        st.subheader("Cashflow Analytics Trend")
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

        st.markdown("---")
        st.subheader("Recent Transactions History Log")
        st.caption("💡 Double-click any cell to manually edit descriptions, change amounts, or override categories on the fly!")
        
        edited_df = st.data_editor(
            df_tx.sort_values(by="Date", ascending=False),
            use_container_width=True,
            num_rows="dynamic",
            key="transaction_editor"
        )
        
        if not edited_df.equals(df_tx):
            st.session_state.transactions = edited_df
            st.rerun()

    # ==============================================================================
    # 🧠 RIGHT COLUMN: AI ASSISTANT PANEL & RUNTIME INSIGHTS
    # ==============================================================================
    with right_grid:
        # Part 1: The Live Chat Interface at the Top Right
        st.subheader("🤖 Live Assistant Interface")
        
        chat_container = st.container(height=350)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                        
        if user_query := st.chat_input("Ask MR.MNY anything about your money..."):
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # (Your deterministic/mock logic engine handles matching here)
            income_val = st.session_state.base_monthly_income
            savings_target = st.session_state.monthly_savings_goal
            spendable_cash = income_val - savings_target
            needs_50 = income_val * 0.50
            wants_30 = income_val * 0.30
            savings_20 = income_val * 0.20
            query_clean = user_query.lower()
            
            if any(k in query_clean for k in ['spend', 'budget', 'salary', 'income', 'money', 'how to']):
                ai_response = f"### 📊 Your Blueprint\n* **Income:** `S$ {income_val:,.2f}`\n* **Savings Goal:** `S$ {savings_target:,.2f}`\n\n1. **Needs (50%):** `S$ {needs_50:,.2f}`\n2. **Wants (30%):** `S$ {wants_30:,.2f}`\n3. **Savings (20%):** `S$ {savings_20:,.2f}`"
            elif any(k in query_clean for k in ['time value', 'tvm', 'value of money']):
                ai_response = "### ⏳ Time Value of Money (TVM)\nMoney available today is worth more than the identical sum in the future due to its potential earning capacity and inflation vectors."
            else:
                ai_response = f"### 💼 Strategy Desk\nAnalyzing query: *\"{user_query}\"*\n* Core Envelope: **S$ {net_balance:,.2f}**\n* Running Target Metric: **S$ {savings_target:,.2f}**"
                
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

        # Part 2: Automated Insights Stacked Nicely Below the Chat
        st.markdown("---")
        st.subheader("✨ AI Suggestions & Insights")
        
        if total_expenses > 1500:
            st.error("**🔴 Shopping Budget Exceeded** Your current monthly expenditure on retail items has surpassed your targeted safety boundary threshold of **S$ 1,000.00**.")
        else:
            st.success("**🟢 Shopping Budget Stable**\nYour spending tracks perfectly below margins.")
            
        st.warning("**🟡 Unusual Velocity Check** An anomalous recurring entertainment charge spike was identified between 2 AM - 4 AM earlier this week.")
        st.info(f"**🟢 On Track for Financial Milestone** At your current localized cash velocity accumulation, your targeted milestone **'Save for Car Downpayment'** will complete 1.4 months early.")
  # =# ==============================================================================
        # 🤖 LIVE ASSISTANT INTERFACE
        # ==============================================================================
       
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                        
        if user_query := st.chat_input("Ask MR.MNY anything about your money..."):
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            current_df = st.session_state.transactions
            expenses_summary = ""
            if not current_df.empty and "Type" in current_df.columns:
                exp_df = current_df[current_df['Type'] == 'Expense']
                if not exp_df.empty:
                    expenses_summary = exp_df.groupby('Category')['Amount'].sum().to_string()

            system_context = f"""
            You are MR.MNY, an elite personal finance manager and wealth strategist.
            The user is seeking personalized, professional financial advice. 

            Here is the user's current live financial profile:
            - Base Monthly Income: S$ {st.session_state.base_monthly_income:,.2f}
            - Target Monthly Savings Goal: S$ {st.session_state.monthly_savings_goal:,.2f}
            - User's Location/Currency Context: Singapore / S$ (Account for local variables if relevant).
            
            Current tracked monthly expenses breakdown by category:
            {expenses_summary if expenses_summary else "No expenses logged yet."}

            Guidelines:
            - Give highly specific advice using their actual numbers.
            - If they ask 'How should I spend my money?', apply professional budgeting rules (like the 50/30/20 rule calibrated to their specific S$ {st.session_state.base_monthly_income} income).
            - Keep your tone premium, sharp, direct, and slightly witty.
            - Format your response beautifully using bolding, lists, and clear headers.
            """

            try:
                from google import genai
                import os
                
                # Automatically retrieves the clean token from your background configuration
                api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                
                if api_key:
                    api_key = api_key.strip().replace('"', '').replace("'", "")
                    
                client = genai.Client(api_key=api_key)
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config={"system_instruction": system_context}
                )
                ai_response = response.text
                
            except Exception as e:
                ai_response = (
                    "⚠️ **AI Engine Connection Notice:** I'm ready to act as your personal finance manager, "
                    "but I need a live connection to the Gemini API. Please make sure your `GEMINI_API_KEY` "
                    "is set up in your environment variables. \n\n"
                    f"*Technical Details:* `{str(e)}`"
                )
                
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(ai_response)
                        
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()
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


# ==============================================================================
# 🎯 VIEW LAYER: GOALS TRACKING (COMPLETED WITH STEP 4)
# ==============================================================================
elif navigation_pane == "🎯 Goals":
    st.title("Financial Goals Management Matrix")
    st.markdown("Set milestones, map targets, and instantly contribute directly to dedicated financial pockets.")
    
    # SUB-PANEL: Create a brand new custom milestone package
    with st.expander("➕ Define New Financial Milestone Target", expanded=False):
        with st.form("new_goal_form", clear_on_submit=True):
            g_name = st.text_input("Goal Milestone Title", placeholder="e.g., Japan Autumn Vacation")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                g_target = st.number_input("Target Goal Amount (S$)", min_value=1.0, value=5000.0, step=100.0)
            with col_f2:
                g_current = st.number_input("Initial Saved Balance (S$)", min_value=0.0, value=0.0, step=50.0)
                
            g_icon = st.selectbox("Pick Target Display Icon", ["✈️", "🚗", "🏠", "🎓", "💻", "💰", "⌚", "💍"])
            
            submit_goal = st.form_submit_button("Create Target Portfolio Entry")
            if submit_goal:
                if g_name.strip() != "":
                    st.session_state.goals.append({
                        "Target": g_name.strip(),
                        "Current": g_current,
                        "Goal": g_target,
                        "Icon": g_icon
                    })
                    st.success(f"🎉 Success! Milestone target pocket '{g_name}' is now active.")
                    st.rerun()
                else:
                    st.error("Please enter a valid milestone title before submitting.")

    st.markdown("### Active Tracking Ledgers")
    
    # Check if any goals exist inside tracking loop arrays
    if not st.session_state.goals:
        st.info("No active milestones mapped. Open the expander panel above to create one!")
    else:
        # Iterate dynamically over editable goals collections arrays
        for idx, g in enumerate(st.session_state.goals):
            # Create a 2-column layout per tracking row (Left for progress visualization, Right for operations)
            col_display, col_actions = st.columns([3, 1])
            
            with col_display:
                pct = min(g["Current"] / g["Goal"], 1.0)
                st.markdown(f"#### {g['Icon']} {g['Target']}")
                st.progress(pct)
                st.markdown(f"**Progress Matrix:** {pct*100:.1f}% filled (`S$ {g['Current']:,}` of `S$ {g['Goal']:,}` tracked elements achieved)")
                
            with col_actions:
                # Aligns inputs down to look proportional beside progress elements
                st.write("") 
                amt_mod = st.number_input(f"Deposit Amount (S$)", min_value=0.0, step=50.0, key=f"add_amt_{idx}")
                
                # Split action column into sub-action rows to support deposit or deletion
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(f"📥 Add Funds", key=f"save_btn_{idx}", use_container_width=True):
                        if amt_mod > 0:
                            st.session_state.goals[idx]["Current"] += amt_mod
                            st.success(f"Deposited S$ {amt_mod}!")
                            st.rerun()
                with btn_col2:
                    if st.button(f"🗑️ Delete", key=f"del_btn_{idx}", use_container_width=True):
                        st.session_state.goals.pop(idx)
                        st.warning("Milestone entry removed from dashboard state tracking portfolios.")
                        st.rerun()
                    
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
