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
    page_title="MR.MNY",  # Updates the browser tab title
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
    # 1. Initialize Income Streams if not present
    if "income_streams" not in st.session_state:
        st.session_state.income_streams = pd.DataFrame([
            {"Source": "Primary Salary", "Amount": 11000.0, "Frequency": "Monthly", "Type": "Salary"}
        ])

    # 2. Initialize Transaction Logs if not present
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
            {"role": "assistant", "content": "Hello Kaur! I'm your **WalletAI** financial assistant powered by Gemini. Ask me anything about your current spending trends, budgets, or ask me to compare categories!"}
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
    st.caption("AI Wealth Desk ")
    st.markdown("---")
    
    navigation_pane = st.radio(
        "Navigation Menu",
        options=["📊 Dashboard", "💸 Expenses", "🎯 Goals", "📈 Investments", "🧮 Calculators"],
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
    
# ⚙️ LIVE PROFILE PARAMETERS WITH MULTI-SOURCE INCOME MANAGER
    with st.expander("⚙️ Adjust Profile Parameters", expanded=True):
        st.subheader("💰 Income Stream Manager")
        
        # 1. Form to add a new income source (Placed at the top for clean workflow)
        with st.form("add_income_form", clear_on_submit=True):
            inc_source = st.text_input("Income Source Name", placeholder="e.g., Condo Rent, Stock Dividend")
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                inc_amt = st.number_input("Amount (S$)", min_value=0.0, step=100.0)
            with col_i2:
                inc_freq = st.selectbox("Frequency", ["Monthly", "Quarterly", "Annually"])
            
            inc_type = st.selectbox("Source Type", ["Salary", "Rental Income", "Dividends", "Side Hustle", "Other"])
            submit_income = st.form_submit_button("➕ Add Income Source")
            
            if submit_income and inc_source.strip():
                new_inc = pd.DataFrame([{
                    "Source": inc_source.strip().capitalize(),
                    "Amount": float(inc_amt),
                    "Frequency": inc_freq,
                    "Type": inc_type
                }])
                st.session_state.income_streams = pd.concat([st.session_state.income_streams, new_inc], ignore_index=True)
                st.success(f"Added {inc_source} successfully!")
                st.rerun()

        st.markdown("---")
        st.caption("📋 Current Active Streams (Double-click any cell to edit or delete)")
        
        # 2. Dynamic Live Data Editor Workspace
        edited_inc_df = st.data_editor(
            st.session_state.income_streams,
            use_container_width=True,
            num_rows="dynamic",  # This allows the user to add/delete rows on the fly
            key="income_streams_editor"
        )
        
        # Safe reactive evaluation checks
        if not edited_inc_df.equals(st.session_state.income_streams):
            st.session_state.income_streams = edited_inc_df
            st.rerun()  # Forces the app to instantly refresh numbers dashboard-wide

        # ==============================================================================
        # 🧮 50/30/20 CALCULATION ENGINE (NORMALIZED TO MONTHLY)
        # ==============================================================================
        # Calculate standardized monthly baseline income from all streams
        total_normalized_monthly_income = 0.0
        for _, row in st.session_state.income_streams.iterrows():
            amt = row["Amount"]
            freq = row["Frequency"]
            if freq == "Monthly":
                total_normalized_monthly_income += amt
            elif freq == "Quarterly":
                total_normalized_monthly_income += (amt / 3)
            elif freq == "Annually":
                total_normalized_monthly_income += (amt / 12)

        # Sync back to base dynamic state variable for dashboard cards
        st.session_state.base_monthly_income = total_normalized_monthly_income

        st.markdown("---")
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
            
        st.markdown("### 📊 50/30/20 Target Strategy")
        needs_alloc = total_normalized_monthly_income * 0.50
        wants_alloc = total_normalized_monthly_income * 0.30
        savings_alloc = total_normalized_monthly_income * 0.20
        
        st.write(f"**Total Monthly Baseline:** S$ {total_normalized_monthly_income:,.2f}")
        st.info(f"🏠 **Needs (50%):** S$ {needs_alloc:,.2f}")
        st.warning(f"🛍️ **Wants (30%):** S$ {wants_alloc:,.2f}")
        st.success(f"📈 **Savings/Invest (20%):** S$ {savings_alloc:,.2f}")
        
        if st.session_state.monthly_savings_goal > savings_alloc:
            st.caption("⚠️ *Note: Your manual savings target outpaces the baseline 20% cushion allocations.*")
    st.markdown("---")
    st.subheader("Preferences")
    toggle_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="sidebar_dark_mode_toggle")
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
        # ==============================================================================
        # 📊 NEW DYNAMIC EXPENSE CATEGORY BREAKDOWN (REPLACES LINE CHART)
        # ==============================================================================
        st.subheader("Monthly Expense Allocation by Category")
        
        expense_only = df_tx[df_tx['Type'] == 'Expense']
        
        if not expense_only.empty:
            # Group actual transactions by category and sum them up cleanly
            cat_summary = expense_only.groupby('Category')['Amount'].sum().reset_index()
            
            # Create a beautiful, scannable horizontal bar chart
            fig_cat_main = px.bar(
                cat_summary.sort_values(by="Amount", ascending=True), 
                x='Amount', 
                y='Category', 
                orientation='h',
                text='Amount',
                color='Amount', 
                color_continuous_scale='Oranges',
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white"
            )
            
            # Format numbers cleanly on top of the bars
            fig_cat_main.update_traces(texttemplate='S$ %{text:,.2f}', textposition='outside')
            fig_cat_main.update_layout(
                height=300, 
                coloraxis_showscale=False, 
                xaxis_title="Total Spent (S$)",
                yaxis_title=None,
                margin=dict(l=20, r=40, t=10, b=10)
            )
            st.plotly_chart(fig_cat_main, use_container_width=True)
        else:
            st.info("💡 No expenses recorded yet. Use the sidebar 'Quick Log' to see your category weights populate here!")
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
        # Part 3: Market Wisdom Corner (Right Corner Placement)
        st.markdown("---")
        st.markdown("### 🏛️ Market Wisdom Corner")
        
        # A curated matrix of professional finance & risk quotes
        quotes_pool = [
            {"quote": "The individual investor should act consistently as an investor and not as a speculator.", "author": "Benjamin Graham"},
            {"quote": "Do not save what is left after spending, but spend what is left after saving.", "author": "Warren Buffett"},
            {"quote": "In investing, what is comfortable is rarely profitable.", "author": "Robert Arnott"},
            {"quote": "The four most dangerous words in investing are: 'This time it's different.'", "author": "Sir John Templeton"},
            {"quote": "An investment in knowledge pays the best interest.", "author": "Benjamin Franklin"},
            {"quote": "Time is your friend; impulse is your enemy. Take advantage of compounding.", "author": "John Bogle"}
        ]
        
        # Smart runtime rotator: uses the current calendar day to automatically cycle the quote 
        # so you see a fresh, premium piece of wisdom every single day you log in.
        import datetime
        current_day_index = datetime.datetime.now().day % len(quotes_pool)
        selected_insight = quotes_pool[current_day_index]
        
        # Render the selected quote inside a sleek callout block structure
        st.markdown(f"""
            > "{selected_insight['quote']}"  
            > — ***{selected_insight['author']}***
        """)


        
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
# 💸 VIEW LAYER: EXPENSES & SPLIT MANAGEMENT
elif navigation_pane == "💸 Expenses":
    st.title("Expense Management & Shared Splits")
    st.markdown("Track individual outlays or calculate shared bill breakdowns with companions.")
    
    # Split the view cleanly into two strategic tabs
    tab_log, tab_split = st.tabs(["📋 Individual Expense Log", "👥 Split Bills Manager"])
    
    # ==============================================================================
    # TAB 1: YOUR EXISTING INDIVIDUAL EXPENSE LOG
    # ==============================================================================
    with tab_log:
        st.subheader("Personal Ledger Overview")
        # (Paste your existing code here that displays st.data_editor or tables for regular transactions)
        st.write(st.session_state.transactions)

    # ==============================================================================
    # 👥 TAB 2: BRAND NEW BILL SPLIT ENGINE
    # ==============================================================================
    with tab_split:
        st.subheader("Shared Group Bill Splitter")
        st.write("Divide group tabs evenly or assign custom debt liabilities between friends.")
        
        # Grid input setup
        col_sp1, col_sp2 = st.columns([1, 1])
        
        with col_sp1:
            with st.form("bill_splitter_form", clear_on_submit=False):
                bill_title = st.text_input("Bill Name / Description", placeholder="e.g., Shatabdi Train Tickets, Group Dinner")
                total_bill = st.number_input("Total Invoice Amount (S$)", min_value=0.0, value=0.0, step=10.0)
                
                # Input list of people splitting the expense
                people_raw = st.text_input("Companions (Comma separated)", value="You, Inderpreet, Parampreet, Bhavika")
                friends_list = [p.strip() for p in people_raw.split(",") if p.strip()]
                num_people = len(friends_list)
                
                split_mode = st.radio("Splitting Strategy Matrix", ["Divide Equally (50/50)", "Custom Percentages Matrix"])
                
                custom_weights = {}
                if split_mode == "Custom Percentages Matrix" and num_people > 0:
                    st.caption("🔧 Allocate exact integer weight percentages per individual (Must equal 100%):")
                    for person in friends_list:
                        custom_weights[person] = st.number_input(f"{person}'s Weight share (%)", min_value=0, max_value=100, value=int(100/num_people), step=5)
                
                submit_split = st.form_submit_button("🧮 Compute Split Share")

        with col_sp2:
            if total_bill > 0 and num_people > 0:
                st.subheader("📋 Final Settlement Matrix")
                
                shares_data = []
                total_percentage_check = 0
                
                for person in friends_list:
                    if split_mode == "Divide Equally (50/50)":
                        person_share = total_bill / num_people
                        shares_data.append({"Individual": person, "Owed Amount (S$)": round(person_share, 2), "Percentage Share": f"{100/num_people:.1f}%"})
                    else:
                        weight = custom_weights.get(person, 0)
                        total_percentage_check += weight
                        person_share = total_bill * (weight / 100)
                        shares_data.append({"Individual": person, "Owed Amount (S$)": round(person_share, 2), "Percentage Share": f"{weight}%"})
                
                # Render results table
                shares_df = pd.DataFrame(shares_data)
                st.dataframe(shares_df, use_container_width=True, hide_index=True)
                
                # Safety check for custom percentages alignment
                if split_mode == "Custom Percentages Matrix" and total_percentage_check != 100:
                    st.error(f"⚠️ Summation Error: Total percentages equal {total_percentage_check}%. It must equal exactly 100% to calculate.")
                else:
                    # Capture "Your" specific liability amount safely
                    your_row = shares_df[shares_df["Individual"].lower().str.contains("you")]
                    your_share_val = your_row["Owed Amount (S$)"].values[0] if not your_row.empty else (total_bill / num_people)
                    
                    st.info(f"💡 **Your Personal Out-Of-Pocket Share:** S$ {your_share_val:,.2f}")
                    
                    # DIRECT ACTION BUTTON: Commits just YOUR share to the main ledger!
                    if st.button("📥 Commit My Share to Expense Ledger", use_container_width=True):
                        if bill_title.strip():
                            new_split_tx = pd.DataFrame([{
                                "Date": datetime.now().strftime("%Y-%m-%d"),
                                "Description": f"[Split] {bill_title.strip().capitalize()}",
                                "Category": "Other",
                                "Amount": float(your_share_val),
                                "Type": "Expense"
                            }])
                            st.session_state.transactions = pd.concat([st.session_state.transactions, new_split_tx], ignore_index=True)
                            st.success(f"Successfully pushed S$ {your_share_val:.2f} into your personal main transaction logs!")
                            st.rerun()
                        else:
                            st.error("Please add a description to log your share.")
            else:
                st.info("Input a bill amount and add names inside the manager form to parse structural shared debt summaries.")
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
                st.write("") 
                amt_mod = st.number_input(f"Transaction Amount (S$)", min_value=0.0, step=50.0, key=f"add_amt_{idx}")
                
                # UPDATED: 3-Column action grid for Deposit, Withdrawal, and Deletion
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    if st.button(f"📥 Add", key=f"save_btn_{idx}", use_container_width=True):
                        if amt_mod > 0:
                            st.session_state.goals[idx]["Current"] += amt_mod
                            st.success(f"Deposited S$ {amt_mod}!")
                            st.rerun()
                            
                with btn_col2:
                    if st.button(f"📤 Out", key=f"withdraw_btn_{idx}", use_container_width=True):
                        if amt_mod > 0:
                            # Safety check: prevent withdrawing more money than what actually exists in the goal pocket
                            if amt_mod <= st.session_state.goals[idx]["Current"]:
                                st.session_state.goals[idx]["Current"] -= amt_mod
                                st.warning(f"Withdrew S$ {amt_mod}!")
                                st.rerun()
                            else:
                                st.error("Insolvent: You cannot withdraw more than this pocket's current balance!")
                                
                with btn_col3:
                    if st.button(f"🗑️", key=f"del_btn_{idx}", use_container_width=True):
                        st.session_state.goals[idx].pop(idx)
                        st.warning("Milestone entry removed from dashboard state tracking portfolios.")
                        st.rerun()
                    
            st.markdown("---")

# 📈 VIEW LAYER: INVESTMENTS PORTFOLIO
elif navigation_pane == "📈 Investments":
    st.title("Asset & Investment Tracking Desk")
    st.markdown("Manage your holdings, analyze market weight allocations, and track compounding performance velocities.")
    
    # 1. INITIALIZE HOLDINGS DATABASE IF NOT PRESENT
    if "portfolio_holdings" not in st.session_state:
        st.session_state.portfolio_holdings = pd.DataFrame([
            {"Asset Ticker": "AAPL", "Asset Class": "Stocks", "Shares Owned": 15.0, "Avg Cost (S$)": 175.00, "Current Price (S$)": 182.40},
            {"Asset Ticker": "NVDA", "Asset Class": "Stocks", "Shares Owned": 25.0, "Avg Cost (S$)": 450.00, "Current Price (S$)": 485.00},
            {"Asset Ticker": "BTC-USD", "Asset Class": "Crypto", "Shares Owned": 0.45, "Avg Cost (S$)": 42000.00, "Current Price (S$)": 64000.00},
            {"Asset Ticker": "CSPX.L", "Asset Class": "S&P 500 ETF", "Shares Owned": 8.0, "Avg Cost (S$)": 490.00, "Current Price (S$)": 525.10}
        ])

    df_p = st.session_state.portfolio_holdings

    # 2. RUN REAL-TIME FINANCIAL PORTFOLIO MATH
    if not df_p.empty:
        df_p["Total Cost"] = df_p["Shares Owned"] * df_p["Avg Cost (S$)"]
        df_p["Current Value"] = df_p["Shares Owned"] * df_p["Current Price (S$)"]
        df_p["Net Profit/Loss"] = df_p["Current Value"] - df_p["Total Cost"]
        
        total_invested = df_p["Total Cost"].sum()
        total_current_value = df_p["Current Value"].sum()
        total_net_gain = total_current_value - total_invested
        gain_percentage = (total_net_gain / total_invested * 100) if total_invested > 0 else 0.0
    else:
        total_invested, total_current_value, total_net_gain, gain_percentage = 0, 0, 0, 0

    # 3. HIGH-END METRIC DISPLAY CARDS
    i_col1, i_col2, i_col3 = st.columns(3)
    with i_col1:
        st.metric(label="Total Portfolio Value", value=f"S$ {total_current_value:,.2f}")
    with i_col2:
        st.metric(label="Invested Principle Capital", value=f"S$ {total_invested:,.2f}")
    with i_col3:
        st.metric(
            label="All-Time Net Returns", 
            value=f"S$ {total_net_gain:,.2f}", 
            delta=f"{gain_percentage:+.2f}% Growth",
            delta_color="normal" if total_net_gain >= 0 else "inverse"
        )

    st.markdown("---")

    # 4. TWO-COLUMN GRID: ANALYTICS VS ASSET MANAGER
    inv_col1, inv_col2 = st.columns([3, 2])
    
    with inv_col1:
        st.subheader("📋 Live Holdings Ledger")
        st.caption("💡 Modify your shares, average costs, or asset classes directly inside the cells below to recalculate metrics instantly.")
        
        # Dynamic portfolio modifier matrix
        edited_portfolio = st.data_editor(
            st.session_state.portfolio_holdings,
            use_container_width=True,
            num_rows="dynamic",
            key="portfolio_sheet_editor"
        )
        if not edited_portfolio.equals(st.session_state.portfolio_holdings):
            st.session_state.portfolio_holdings = edited_portfolio
            st.rerun()

        # Cumulative Growth Trend Analysis (Uses clean 'ME' string to avoid layout crashes)
        st.subheader("📈 Aggregated Equity Compounding Trend")
        timeline_idx = pd.date_range(end=datetime.now(), periods=6, freq='ME')
        perf_mock = pd.DataFrame({
            'Timeline': timeline_idx,
            'Value Portfolio Growth (S$)': [total_current_value * 0.85, total_current_value * 0.92, total_current_value * 0.89, total_current_value * 0.96, total_current_value * 0.98, total_current_value]
        })
        fig_perf = px.area(perf_mock, x='Timeline', y='Value Portfolio Growth (S$)', 
                           color_discrete_sequence=['#16a085'], template="plotly_white")
        fig_perf.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_perf, use_container_width=True)
        
    with inv_col2:
        st.subheader("🎯 Target Asset Allocation Weighting")
        if not df_p.empty:
            # Aggregate weighting sums by asset category grouping boundaries
            allocation_summary = df_p.groupby("Asset Class")["Current Value"].sum().reset_index()
            fig_holdings = px.pie(
                allocation_summary, 
                values='Current Value', 
                names='Asset Class', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_holdings.update_layout(height=280, showlegend=True, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_holdings, use_container_width=True)
            
            # Subheader bar for individual ticker concentrations
            st.subheader("🎟️ Position Concentration Weights")
            fig_ticker = px.bar(
                df_p, x='Asset Ticker', y='Current Value',
                color='Asset Class', color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_ticker.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_ticker, use_container_width=True)
        else:
            st.info("Add entries to the ledger to construct performance allocation charts.")



# 🧮 VIEW LAYER: MATH CALCULATORS (EMI & SIP)
elif navigation_pane == "🧮 Calculators":
    st.title("Financial Planning Calculators")
    st.markdown("Run scenarios for future investments or analyze debt liability structures.")
    
    # Create two clean, spacious layout tabs
    tab_sip, tab_emi = st.tabs(["📈 SIP Wealth Accumulator", "🚗/🏠 EMI Loan Planner"])
    
    # ==============================================================================
    # 📈 TAB 1: SYSTEMATIC INVESTMENT PLAN (SIP) CALCULATOR
    # ==============================================================================
    with tab_sip:
        st.subheader("Systematic Investment Plan (SIP) Compounder")
        st.write("Calculate how much wealth you can accumulate over time with regular monthly contributions.")
        
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            sip_monthly = st.number_input("Monthly SIP Contribution (S$)", min_value=10, value=500, step=50, key="sip_m_input")
            sip_rate = st.slider("Expected Annual Return Rate (%)", min_value=1.0, max_value=25.0, value=12.0, step=0.5, key="sip_r_slider")
            sip_years = st.slider("Investment Horizon (Years)", min_value=1, max_value=40, value=10, step=1, key="sip_y_slider")
            
            # SIP Formula Logic
            # Formula: M = P * [((1 + i)^n - 1) / i] * (1 + i)
            # where i = monthly return rate, n = total months
            i = (sip_rate / 100) / 12
            n = sip_years * 12
            
            total_invested_sip = sip_monthly * n
            future_value_sip = sip_monthly * (((1 + i)**n - 1) / i) * (1 + i)
            wealth_gained_sip = future_value_sip - total_invested_sip
            
        with col_s2:
            # Display results in high-end structural summary metric columns
            sm_col1, sm_col2, sm_col3 = st.columns(3)
            with sm_col1:
                st.metric("Total Invested Principle", f"S$ {total_invested_sip:,.0f}")
            with sm_col2:
                st.metric("Estimated Wealth Gain", f"S$ {wealth_gained_sip:,.0f}")
            with sm_col3:
                st.metric("Total Target Wealth", f"S$ {future_value_sip:,.0f}")
                
            # Render a beautiful visual breakdown pie chart
            sip_pie_df = pd.DataFrame({
                "Component": ["Invested Capital", "Compounded Returns"],
                "Amount": [total_invested_sip, wealth_gained_sip]
            })
            fig_sip = px.pie(sip_pie_df, values="Amount", names="Component", hole=0.4,
                             color_discrete_sequence=["#1abc9c", "#2c3e50"], template="plotly_white")
            fig_sip.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_sip, use_container_width=True)

    # ==============================================================================
    # 🚗/🏠 TAB 2: EQUATED MONTHLY INSTALLMENT (EMI) CALCULATOR
    # ==============================================================================
    with tab_emi:
        st.subheader("Equated Monthly Installment (EMI) Debt Planner")
        st.write("Determine your structural monthly payment liabilities for home, car, or personal loans.")
        
        col_e1, col_e2 = st.columns([1, 2])
        
        with col_e1:
            loan_principle = st.number_input("Principal Loan Amount (S$)", min_value=1000, value=50000, step=5000, key="emi_p_input")
            loan_rate = st.slider("Interest Rate (Annual %)", min_value=0.5, max_value=15.0, value=3.5, step=0.1, key="emi_r_slider")
            loan_years = st.slider("Loan Tenure (Years)", min_value=1, max_value=30, value=5, step=1, key="emi_y_slider")
            
            # Standard Reducing Balance EMI Formula Logic
            # Formula: EMI = [P * r * (1 + r)^n] / [((1 + r)^n) - 1]
            # where r = monthly interest rate, n = total tenure months
            r = (loan_rate / 100) / 12
            num_months = loan_years * 12
            
            if r > 0:
                monthly_emi = (loan_principle * r * (1 + r)**num_months) / (((1 + r)**num_months) - 1)
            else:
                monthly_emi = loan_principle / num_months
                
            total_repayment = monthly_emi * num_months
            total_interest_payable = total_repayment - loan_principle
            
        with col_e2:
            # Display metrics panel
            em_col1, em_col2, em_col3 = st.columns(3)
            with em_col1:
                st.metric("Monthly EMI Outflow", f"S$ {monthly_emi:,.2f}")
            with em_col2:
                st.metric("Principal Loan Amount", f"S$ {loan_principle:,.0f}")
            with em_col3:
                st.metric("Total Interest Outlay", f"S$ {total_interest_payable:,.0f}")
                
            # Render visual debt allocation breakdown pie chart
            emi_pie_df = pd.DataFrame({
                "Component": ["Principal Capital", "Interest Liability"],
                "Amount": [loan_principle, total_interest_payable]
            })
            fig_emi = px.pie(emi_pie_df, values="Amount", names="Component", hole=0.4,
                             color_discrete_sequence=["#e74c3c", "#34495e"], template="plotly_white")
            fig_emi.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_emi, use_container_width=True)
            
            # Budget Integration Check Statement
            st.markdown("---")
            if monthly_emi > (st.session_state.get('base_monthly_income', 5500) * 0.50):
                st.error(f"⚠️ **High Risk Outflow Warning:** This single EMI liability (S$ {monthly_emi:,.2f}) swallows up more than **50%** of your active monthly income profile standard boundaries. Proceed with caution!")
            else:
                st.success(f"🟢 **Safe Boundary Validation:** This EMI liability accounts for {(monthly_emi / st.session_state.get('base_monthly_income', 5500) * 100):.1f}% of your dynamic income pool, mapping safely within regular risk indices.")
