import streamlit as st
import pandas as pd
from datetime import datetime, date
import altair as alt

# --- 1. PAGE CONFIGURATION & INTERFACE CLEAN-UP (Must be at the absolute top) ---
st.set_page_config(
    page_title="Custom Trade Diary", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Heavy-duty CSS block to hide GitHub icon, top headers, deployment buttons, and footers
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    /* Completely removes the top deployment toolbar and GitHub code tracking buttons */
    div[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    button[title="View source code"] {display: none !important;}
    
    /* Hides the floating Streamlit badge icon on mobile and web viewports */
    .viewerBadge_container__1QSob {display: none !important;}
    div[class^="viewerBadge_"] {display: none !important;}
    iframe[title="Managed Hosting Badge"] {display: none !important;}
    
    /* Adjusts the top layout padding space where the header used to sit */
    .styles_borderWrapper__lCvak {border: none !important;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0) !important; text-indent: -99999px !important;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)


# --- 2. DATABASE IN-MEMORY INITIALIZATION ---
# Simulated database system to keep accounts separate
if "user_database" not in st.session_state:
    st.session_state.user_database = {
        "abhijeet@gmail.com": {"password": "SmcTrader2026", "name": "Abhijeet"}
    }

# Tracks logged-in profile metrics
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# System memory allocation per individual profile
if "user_data_stores" not in st.session_state:
    st.session_state.user_data_stores = {}


# --- 3. GATEWAY AUTHENTICATION CONTROLLER ---
def render_auth_gateway():
    st.markdown("""
        <style>
        .auth-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        h2 { text-align: center; color: #1E3A8A; margin-bottom: 1.5rem; }
        </style>
    """, unsafe_allow_html=True)
    
    st.write("## 🔒 Trade Diary Gateway")
    
    # Selection tabs for logging in vs building an account profile
    tab_login, tab_signup = st.tabs(["🔑 Account Login", "📝 Create New Profile"])
    
    with tab_login:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        login_email = st.text_input("Registered Email Address", key="login_email_input", placeholder="name@example.com").strip().lower()
        login_password = st.text_input("Password Verification", type="password", key="login_pass_input", placeholder="••••••••")
        
        if st.button("Unlock My Dashboard", use_container_width=True):
            if login_email in st.session_state.user_database and st.session_state.user_database[login_email]["password"] == login_password:
                st.session_state.logged_in_user = login_email
                st.success(f"Welcome back, {st.session_state.user_database[login_email]['name']}! Synchronizing history metrics...")
                st.rerun()
            else:
                st.error("Authentication check failed. Please verify credentials or create an account template profile.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_signup:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        new_name = st.text_input("Trader Name / Nickname", placeholder="Alex")
        new_email = st.text_input("Your Email Address", key="signup_email_input", placeholder="alex@trading.com").strip().lower()
        new_password = st.text_input("Create Secure Access Password", type="password", key="signup_pass_input", placeholder="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Access Password", type="password", placeholder="Repeat your password")
        
        if st.button("Register & Initialize Journal", use_container_width=True):
            if not new_name or not new_email or not new_password:
                st.error("All processing profile input blocks must be populated.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif new_email in st.session_state.user_database:
                st.error("An account configuration profile already exists matching this email pointer.")
            else:
                # Add to memory user file structure mapping layouts
                st.session_state.user_database[new_email] = {"password": new_password, "name": new_name}
                st.success("Registration verification confirmed! You can now log in under the Login tab setup.")


# --- 4. APPLICATION PROCESS ROUTING CORNER ---
if st.session_state.logged_in_user is None:
    render_auth_gateway()
else:
    current_email = st.session_state.logged_in_user
    user_profile = st.session_state.user_database[current_email]
    
    # Initialize the specific logged-in user's data isolated file structure
    if current_email not in st.session_state.user_data_stores:
        st.session_state.user_data_stores[current_email] = {
            "trades": pd.DataFrame(columns=["Date", "Pair", "Direction", "Entry", "SL", "TP", "P&L", "Status", "Reason"]),
            "rules": [
                "Waited for higher timeframe (4H) trend alignment?",
                "Liquidity swept before entry?",
                "15M Market Structure Shift (MSS) or Change of Character (CHoCH) confirmed?",
                "Entry placed strictly at the valid Order Block (1M/15M)?",
                "Risk managed correctly? (Max 1-2% per trade)"
            ]
        }
    
    # Shortcuts to current profile storage instances
    user_trades = st.session_state.user_data_stores[current_email]["trades"]
    user_rules = st.session_state.user_data_stores[current_email]["rules"]

    # Sidebar Navigation System Layout
    st.sidebar.markdown(f"### 👋 Welcome, **{user_profile['name']}**")
    st.sidebar.caption(f"Profile: {current_email}")
    if st.sidebar.button("🚪 Close Workspace (Logout)", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.title("📈 Navigation Menu")
    menu = st.sidebar.radio(
        "Go To",
        ["Dashboard", "Live Challenge", "Calendar", "Log New Trade", "My Rules Templates"]
    )

    # 1. DASHBOARD COMPONENT
    if menu == "Dashboard":
        st.title("📊 Trading Dashboard")
        total_trades = len(user_trades)
        
        if total_trades > 0:
            total_pl = user_trades["P&L"].sum()
            wins = len(user_trades[user_trades["Status"] == "Win"])
            win_rate = (wins / total_trades) * 100
        else:
            total_pl = 0.0
            win_rate = 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric("TOTAL P&L", f"₹{total_pl:,.2f}", delta=f"{'🟢' if total_pl >= 0 else '🔴'}")
        col2.metric("WIN RATE", f"{win_rate:.1f}%")
        col3.metric("TOTAL TRADES", total_trades)
        
        st.markdown("---")
        st.subheader("🗓️ Performance by Day")
        if total_trades > 0:
            user_trades['Day_of_Week'] = pd.to_datetime(user_trades['Date']).dt.day_name()
            day_stats = user_trades.groupby('Day_of_Week').agg(
                Total_PL=('P&L', 'sum'),
                Trades=('Status', 'count'),
                Wins=('Status', lambda x: (x == 'Win').sum())
            ).reset_index()
            day_stats['Win_Rate_%'] = (day_stats['Wins'] / day_stats['Trades']) * 100
            
            chart = alt.Chart(day_stats).mark_bar().encode(
                x='Day_of_Week:N',
                y='Win_Rate_%:Q',
                color=alt.value("#29b5e8")
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No trades logged yet. Go to 'Log New Trade' to add your first setup!")

    # 2. LIVE CHALLENGE COMPONENT
    elif menu == "Live Challenge":
        st.title("🎯 Capital Growth Challenge")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", date(2026, 6, 10))
            end_date = st.date_input("Target Date", date(2026, 6, 15))
        with col2:
            target_amt = st.number_input("Target Profit ($)", value=15.0)
            current_profit = st.number_input("Current Profit Accrued ($)", value=0.0)

        today = date(2026, 6, 15)
        days_remaining = (end_date - today).days if end_date >= today else 0
        remaining_target = max(target_amt - current_profit, 0.0)
        daily_needed = remaining_target / days_remaining if days_remaining > 0 else remaining_target

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Days Remaining", f"{days_remaining} Days")
        c2.metric("Remaining Target", f"${remaining_target:.2f}")
        c3.metric("Adjusted Daily Target", f"${daily_needed:.2f}/day")
        
        progress_pct = min(int((current_profit / target_amt) * 100), 100) if target_amt > 0 else 0
        st.write(f"**Challenge Progress: {progress_pct}% Completed**")
        st.progress(progress_pct / 100)

    # 3. CALENDAR COMPONENT
    elif menu == "Calendar":
        st.title("📅 Trading Calendar View")
        st.markdown("""
        <style>
        .calendar-box { border: 1px solid #ddd; border-radius: 5px; padding: 15px; text-align: center; background-color: #f9f9f9; min-height: 80px;}
        .green-day { background-color: #d4edda !important; color: #155724; font-weight: bold; }
        .red-day { background-color: #f8d7da !important; color: #721c24; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)
        st.write("### June 2026")
        
        row1 = st.columns(7)
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for idx, col in enumerate(row1):
            col.write(f"**{days[idx]}**")
            
        row2 = st.columns(7)
        row2[0].markdown('<div class="calendar-box"></div>', unsafe_allow_html=True)
        row2[1].markdown('<div class="calendar-box">1<br><small>₹0</small></div>', unsafe_allow_html=True)
        row2[2].markdown('<div class="calendar-box green-day">2<br><small>+₹500</small></div>', unsafe_allow_html=True)
        row2[3].markdown('<div class="calendar-box">3<br><small>₹0</small></div>', unsafe_allow_html=True)
        row2[4].markdown('<div class="calendar-box red-day">4<br><small>-₹250</small></div>', unsafe_allow_html=True)
        row2[5].markdown('<div class="calendar-box">5<br><small>₹0</small></div>', unsafe_allow_html=True)
        row2[6].markdown('<div class="calendar-box">6<br><small>₹0</small></div>', unsafe_allow_html=True)

    # 4. LOG NEW TRADE COMPONENT
    elif menu == "Log New Trade":
        st.title("📝 Journal a New Trade Entry")
        st.warning("⚠️ CRITICAL COMPLIANCE: Verify your trading execution rules below before submitting!")
        
        rule_checks = []
        for rule in user_rules:
            rule_checks.append(st.checkbox(rule, key=f"check_{rule}"))
            
        all_rules_passed = all(rule_checks)
        st.markdown("---")
        
        with st.form("trade_form"):
            col1, col2, col3 = st.columns(3)
            trade_date = col1.date_input("Trade Date", date.today())
            pair = col2.text_input("Asset/Pair", "EURUSD")
            direction = col3.selectbox("Direction", ["Long", "Short"])
            
            col4, col5, col6, col7 = st.columns(4)
            entry_p = col4.number_input("Entry Price", value=0.0, format="%.5f")
            sl_p = col5.number_input("Stop Loss", value=0.0, format="%.5f")
            tp_p = col6.number_input("Take Profit", value=0.0, format="%.5f")
            pl_val = col7.number_input("Net P&L Realized (₹)", value=0.0)
            
            status = st.selectbox("Outcome Status", ["Win", "Loss", "Breakeven"])
            reason = st.text_area("Market Analysis Notes & Confluence Reason")
            
            submit = st.form_submit_button("Lock & Save Trade Details")
            
            if submit:
                if not all_rules_passed:
                    st.error("🛑 RULE VIOLATION DETECTED! Satisfy all rules confluences first.")
                else:
                    new_row = {
                        "Date": str(trade_date), "Pair": pair, "Direction": direction,
                        "Entry": entry_p, "SL": sl_p, "TP": tp_p, "P&L": pl_val,
                        "Status": status, "Reason": reason
                    }
                    st.session_state.user_data_stores[current_email]["trades"] = pd.concat([user_trades, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("🎯 Trade logged securely to your personal account profile history!")
                    st.rerun()

    # 5. CUSTOM RULES TEMPLATES COMPONENT
    elif menu == "My Rules Templates":
        st.title("🛡️ Trading Rules & Discipline Strategy")
        new_rule = st.text_input("Add a core operational rule:")
        if st.button("Add Strategy Rule") and new_rule:
            st.session_state.user_data_stores[current_email]["rules"].append(new_rule)
            st.success("New operational rule saved!")
            st.rerun()
            
        st.write("### Current Active Rules:")
        for idx, rule in enumerate(user_rules):
            st.write(f"**{idx+1}.** {rule}")
