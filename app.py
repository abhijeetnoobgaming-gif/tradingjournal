import streamlit as st
from datetime import date

# --- 1. PAGE CONFIG & HIDE DEFAULT UI ---
st.set_page_config(page_title="Trade Diary", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* CUSTOM HAMBURGER BUTTON (TOP LEFT) */
    .hamburger-btn {
        position: fixed;
        top: 15px;
        left: 15px;
        z-index: 999999;
        cursor: pointer;
        background: #1e1e1e;
        padding: 8px 10px;
        border-radius: 6px;
        border: 1px solid #333;
        display: flex;
        flex-direction: column;
        gap: 4px;
        transition: 0.3s;
    }
    .hamburger-btn:hover { background: #333; }
    .line { width: 22px; height: 2px; background: white; border-radius: 2px; }

    /* SIDEBAR STYLING (Gemini Dark Theme) */
    [data-testid="stSidebar"] {
        background-color: #131314 !important;
        width: 260px !important;
    }
    .nav-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        color: white;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
    }
    </style>

    <!-- The 3-Line Icon HTML -->
    <div class="hamburger-btn" id="menu-toggle" onclick="window.parent.document.querySelector('button[data-testid=\'stSidebarCollapseButton\']').click()">
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
    </div>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 💠 Trade Diary")
    
    # Simple navigation logic
    selection = st.radio(
        "Navigation",
        ["Dashboard", "Trade Entry", "Calendar"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("v1.0.2 • Connected")

# --- 3. PAGE LOGIC ---
if selection == "Dashboard":
    st.title("📈 Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Profit", "+$1,420", "12%")
    c2.metric("Win Rate", "68%", "2%")
    c3.metric("Balance", "$12,400")
    
    st.divider()
    st.subheader("Recent Activity")
    st.info("Your performance is up 5% compared to last week.")

elif selection == "Trade Entry":
    st.title("📝 New Trade")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        col1.text_input("Symbol", placeholder="e.g. BTCUSDT")
        col2.selectbox("Side", ["Long", "Short"])
        st.number_input("Entry Price", step=0.01)
        st.button("Submit Trade", use_container_width=True)

elif selection == "Calendar":
    st.title("📅 Trading Calendar")
    st.date_input("Filter by Date", date.today())
    
    # Simple table to represent a calendar log
    st.table({
        "Date": ["2023-10-01", "2023-10-02"],
        "Trades": [4, 2],
        "PnL": ["+$200", "-$50"]
    })

# --- 4. JS AUTO-SIDEBAR FIX ---
# This ensures clicking the 3 lines always triggers the sidebar expand
st.components.v1.html("""
<script>
    const parentDoc = window.parent.document;
    const btn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]');
    // Hide the native Streamlit button but keep it clickable via our icon
    if(btn) {
        btn.style.opacity = "0";
    }
</script>
""", height=0)
