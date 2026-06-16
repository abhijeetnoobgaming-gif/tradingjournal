import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Trade Diary", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM UI (HAMBURGER & SIDEBAR) ---
st.markdown("""
    <style>
    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* Custom Floating Hamburger */
    .menu-trigger {
        position: fixed;
        top: 15px;
        left: 15px;
        z-index: 99999;
        cursor: pointer;
        background: #1E3A8A;
        padding: 10px;
        border-radius: 5px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .bar { width: 20px; height: 2px; background: white; border-radius: 2px; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    </style>

    <div class="menu-trigger" onclick="window.parent.document.querySelector('button[data-testid=\'sidebar-toggle\']').click()">
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
    </div>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True # Set to True for demonstration

# --- 4. NAVIGATION & PAGES ---
def main():
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    
    # Menu Options
    page = st.sidebar.radio(
        "GO TO:",
        ["Dashboard", "Trade Log", "Calendar"],
        label_visibility="collapsed"
    )

    if page == "Dashboard":
        st.title("📈 Performance Dashboard")
        col1, col2, col3 = st.columns(3)
        col1.metric("Net PnL", "$1,250")
        col2.metric("Win Rate", "65%")
        col3.metric("Trades", "24")

    elif page == "Trade Log":
        st.title("📝 Log Your Trades")
        with st.form("entry_form"):
            c1, c2 = st.columns(2)
            c1.text_input("Asset Symbol")
            c1.number_input("Entry Price")
            c2.selectbox("Position", ["Long", "Short"])
            c2.number_input("Quantity")
            st.form_submit_button("Save Trade")

    elif page == "Calendar":
        st.title("📅 Trading Calendar")
        # Simplified Calendar View
        d = st.date_input("Select Date to View Trades", date.today())
        st.info(f"Viewing history for {d}")
        # Dummy data
        st.table(pd.DataFrame({
            'Time': ['10:30', '14:15'],
            'Symbol': ['BTC', 'ETH'],
            'PnL': ['+$200', '-$50']
        }))

    # Logout at bottom of sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. AUTH GATE ---
if st.session_state.logged_in:
    main()
else:
    st.title("Please Login")
    if st.button("Enter App"):
        st.session_state.logged_in = True
        st.rerun()
