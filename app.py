import streamlit as st
import pandas as pd

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Personal Finance Assistant",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# SESSION STATE
# Keeps chat history alive across reruns
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# MOCK AI FUNCTION
# Replace with OpenAI/Gemini API later if desired
# ============================================================
def get_finance_advice(query):
    """
    Prototype financial advisor logic.

    Replace this section with OpenAI/Gemini API calls
    when moving from prototype to production.
    """

    q = query.lower()

    if "compound interest" in q:
        return {
            "title": "📈 Understanding Compound Interest",
            "response": (
                "Compound interest means earning interest on both your original "
                "investment and the interest already earned. Starting early is "
                "one of the most powerful ways to build wealth."
            ),
            "tip": "Even small monthly investments can grow significantly over time."
        }

    elif "debt" in q or "loan" in q:
        return {
            "title": "💳 Debt Management Guidance",
            "response": (
                "Focus on paying high-interest debt first while continuing "
                "minimum payments on other obligations. Avoid taking on new debt "
                "unless necessary."
            ),
            "tip": "Create a repayment plan and track progress monthly."
        }

    elif "budget" in q:
        return {
            "title": "📊 Budgeting Advice",
            "response": (
                "A simple budgeting framework is the 50/30/20 rule:\n"
                "- 50% Needs\n"
                "- 30% Wants\n"
                "- 20% Savings & Investments"
            ),
            "tip": "Review your budget at least once per month."
        }

    elif "snowball" in q:
        return {
            "title": "❄️ Snowball vs Avalanche",
            "response": (
                "Snowball Method: Pay smallest balances first for motivation.\n\n"
                "Avalanche Method: Pay highest interest rates first to save money."
            ),
            "tip": "Avalanche saves more money, Snowball often improves consistency."
        }

    elif "saving" in q or "savings" in q:
        return {
            "title": "🏦 Savings Strategy",
            "response": (
                "Build an emergency fund covering 3–6 months of expenses. "
                "Automate transfers to savings whenever possible."
            ),
            "tip": "Treat savings like a recurring bill."
        }

    else:
        return {
            "title": "💡 Personal Finance Guidance",
            "response": (
                "Financial wellness starts with budgeting, reducing high-interest "
                "debt, building savings, and investing consistently."
            ),
            "tip": "Small consistent actions often outperform occasional big changes."
        }


# ============================================================
# HEADER
# ============================================================
st.title("💰 Personal Finance Assistant")
st.caption(
    "Your Finance Minister for smarter budgeting, savings, and debt management."
)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    st.header("🏛️ Finance Minister")

    page = st.radio(
        "Navigation",
        [
            "Assistant",
            "Dashboard",
            "About"
        ]
    )

    st.divider()

    financial_literacy = st.toggle(
        "📚 Financial Literacy Mode",
        value=True
    )

    st.divider()

    st.markdown("### Quick Topics")
    st.write(
        """
        • Budgeting  
        • Savings  
        • Debt Management  
        • Compound Interest  
        • Financial Habits
        """
    )

# ============================================================
# ABOUT PAGE
# ============================================================
if page == "About":

    st.header("About This Prototype")

    st.markdown("""
    ### Personal Finance Assistant

    This Streamlit application demonstrates how AI can help users:

    - Build savings habits
    - Manage debt responsibly
    - Understand budgeting
    - Improve financial literacy

    ### Technology Stack

    - Streamlit
    - Python
    - Pandas
    - Session State

    ### Future Enhancements

    - OpenAI Integration
    - Gemini Integration
    - Personalized Budget Tracking
    - Investment Education
    - Financial Goal Planning

    Developed as a GitHub + Streamlit Cloud deployable prototype.
    """)

# ============================================================
# DASHBOARD PAGE
# ============================================================
elif page == "Dashboard":

    st.header("📊 Financial Dashboard")

    # -------------------------
    # METRICS
    # -------------------------
    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            label="Monthly Income",
            value="$4,000"
        )

    with metric_col2:
        st.metric(
            label="Savings Goal",
            value="$800"
        )

    with metric_col3:
        st.metric(
            label="Debt Remaining",
            value="$2,500"
        )

    st.divider()

    # -------------------------
    # 50/30/20 BUDGET CHART
    # -------------------------
    st.subheader("50 / 30 / 20 Budget Rule")

    budget_df = pd.DataFrame({
        "Category": ["Needs", "Wants", "Savings"],
        "Percent": [50, 30, 20]
    })

    st.bar_chart(
        budget_df.set_index("Category")
    )

    st.info(
        "A common budgeting framework: 50% Needs, 30% Wants, 20% Savings."
    )

# ============================================================
# ASSISTANT PAGE
# ============================================================
else:

    st.header("🤖 Financial Assistant")

    # --------------------------------------------------------
    # FINANCIAL LITERACY MODE
    # --------------------------------------------------------
    if financial_literacy:
        with st.expander("📚 Financial Literacy Tip"):
            st.write(
                """
                Financial literacy is the ability to understand and effectively
                use financial skills such as budgeting, saving, investing,
                and debt management.
                """
            )

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------
    st.subheader("⚡ Quick Actions")

    qa_col1, qa_col2 = st.columns(2)

    if qa_col1.button("📈 Explain Compound Interest"):
        response = get_finance_advice("compound interest")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"**{response['title']}**\n\n{response['response']}\n\n💡 {response['tip']}"
            }
        )

    if qa_col2.button("❄️ Snowball vs Avalanche"):
        response = get_finance_advice("snowball")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"**{response['title']}**\n\n{response['response']}\n\n💡 {response['tip']}"
            }
        )

    st.divider()

    # --------------------------------------------------------
    # CHAT HISTORY CONTAINER
    # --------------------------------------------------------
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # --------------------------------------------------------
    # USER INPUT
    # --------------------------------------------------------
    user_query = st.chat_input(
        "Ask about budgeting, savings, or debt management..."
    )

    if user_query:

        # Store user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_query
            }
        )

        # Generate AI response
        advice = get_finance_advice(user_query)

        assistant_message = (
            f"### {advice['title']}\n\n"
            f"{advice['response']}\n\n"
            f"💡 **Tip:** {advice['tip']}"
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_message
            }
        )

        st.rerun()

# ============================================================
# FOOTER
# ============================================================
st.divider()

st.caption(
    "⚠️ Educational prototype only. Not financial, legal, or investment advice."
)

# ============================================================
# OPTIONAL OPENAI INTEGRATION TEMPLATE
# ============================================================
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_finance_advice(query):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content":"You are a helpful financial literacy assistant."
            },
            {
                "role":"user",
                "content":query
            }
        ]
    )

    return response.choices[0].message.content
"""
