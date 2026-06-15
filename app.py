import streamlit as st
import pandas as pd
from datetime import datetime, date
import altair as alt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Custom Trade Diary", layout="wide", initial_sidebar_state="expanded")

# --- MOCK DATA / SESSION STATE ---
# This holds your data while the app runs. Later we can connect it to a file.
if 'trades' not in st.session_state:
    st.session_state.trades = pd.DataFrame(columns=[
        "Date", "Pair", "Direction", "Entry", "SL", "TP", "P&L", "Status", "Reason"
    ])

if 'rules' not in st.session_state:
    st.session_state.rules = [
        "Waited for higher timeframe (4H) trend alignment?",
        "Liquidity swept before entry?",
        "15M Market Structure Shift (MSS) or Change of Character (CHoCH) confirmed?",
        "Entry placed strictly at the valid Order Block (1M/15M)?",
        "Risk managed correctly? (Max 1-2% per trade)"
    ]

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📈 Trade Diary")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Go To",
    ["Dashboard", "Live Challenge", "Calendar", "Log New Trade", "My Rules Templates"]
)

# --- APP LOGIC ---

# 1. DASHBOARD
if menu == "Dashboard":
    st.title("📊 Trading Dashboard")
    st.subheader("Your performance at a glance")
    
    # Summary Metrics
    trades_df = st.session_state.trades
    total_trades = len(trades_df)
    
    if total_trades > 0:
        total_pl = trades_df["P&L"].sum()
        wins = len(trades_df[trades_df["Status"] == "Win"])
        win_rate = (wins / total_trades) * 100
    else:
        total_pl = 0.0
        win_rate = 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL P&L", f"${total_pl:,.2f}", delta=f"{'🟢' if total_pl >= 0 else '🔴'}")
    col2.metric("WIN RATE", f"{win_rate:.1f}%")
    col3.metric("TOTAL TRADES", total_trades)
    
    st.markdown("---")
    
    # Best Trading Days Analysis
    st.subheader("🗓️ Performance by Day")
    if total_trades > 0:
        trades_df['Day_of_Week'] = pd.to_datetime(trades_df['Date']).dt.day_name()
        day_stats = trades_df.groupby('Day_of_Week').agg(
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


# 2. LIVE CHALLENGE
elif menu == "Live Challenge":
    st.title("🎯 Capital Growth Challenge")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", date(2026, 6, 10))
        end_date = st.date_input("Target Date", date(2026, 6, 15))
    with col2:
        target_amt = st.number_input("Target Profit ($)", value=15.0)
        current_profit = st.number_input("Current Profit Accrued ($)", value=0.0)

    # Dynamic target calculation logic
    today = date(2026, 6, 15)  # Evaluated matching current session scope
    days_total = (end_date - start_date).days + 1
    days_remaining = (end_date - today).days if end_date >= today else 0
    
    remaining_target = target_amt - current_profit
    if remaining_target < 0:
        remaining_target = 0
        
    daily_needed = remaining_target / days_remaining if days_remaining > 0 else remaining_target

    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Days Remaining", f"{days_remaining} Days")
    c2.metric("Remaining Target", f"${remaining_target:.2f}")
    c3.metric("Adjusted Daily Target", f"${daily_needed:.2f}/day")
    
    # Progress Bar
    progress_pct = min(int((current_profit / target_amt) * 100), 100) if target_amt > 0 else 0
    st.write(f"**Challenge Progress: {progress_pct}% Completed**")
    st.progress(progress_pct / 100)


# 3. CALENDAR VIEW
elif menu == "Calendar":
    st.title("📅 Trading Calendar View")
    st.write("Keep track of your daily wins and losses over the month.")
    
    # Simple interactive simulator matching your mockup calendar block
    selected_month = st.selectbox("Select Month", ["June 2026", "May 2026"])
    
    # Generate mock calendar grid rows
    st.markdown("""
    <style>
    .calendar-box { border: 1px solid #ddd; border-radius: 5px; padding: 15px; text-align: center; background-color: #f9f9f9; min-height: 80px;}
    .green-day { background-color: #d4edda !important; color: #155724; font-weight: bold; }
    .red-day { background-color: #f8d7da !important; color: #721c24; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    st.write("### June 2026")
    
    # Visual grid representation
    row1 = st.columns(7)
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for idx, col in enumerate(row1):
        col.write(f"**{days[idx]}**")
        
    row2 = st.columns(7)
    row2[0].markdown('<div class="calendar-box"></div>', unsafe_allow_html=True)
    row2[1].markdown('<div class="calendar-box">1<br><small>$0</small></div>', unsafe_allow_html=True)
    row2[2].markdown('<div class="calendar-box green-day">2<br><small>+$5.50</small></div>', unsafe_allow_html=True)
    row2[3].markdown('<div class="calendar-box">3<br><small>$0</small></div>', unsafe_allow_html=True)
    row2[4].markdown('<div class="calendar-box red-day">4<br><small>-$2.00</small></div>', unsafe_allow_html=True)
    row2[5].markdown('<div class="calendar-box">5<br><small>$0</small></div>', unsafe_allow_html=True)
    row2[6].markdown('<div class="calendar-box">6<br><small>$0</small></div>', unsafe_allow_html=True)


# 4. LOG NEW TRADE
elif menu == "Log New Trade":
    st.title("📝 Journal a New Trade Entry")
    
    st.warning("⚠️ CRITICAL COMPLIANCE: Verify your trading execution rules below before submitting!")
    rule_checks = []
    for rule in st.session_state.rules:
        rule_checks.append(st.checkbox(rule))
        
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
        pl_val = col7.number_input("Net P&L Realized ($)", value=0.0)
        
        status = st.selectbox("Outcome Status", ["Win", "Loss", "Breakeven"])
        reason = st.text_area("Market Analysis Notes & Confluence Reason", placeholder="Explain structure validation, liquidity sweep confirmation details...")
        
        submit = st.form_submit_submit = st.form_submit_button("Lock & Save Trade Details")
        
        if submit:
            if not all_rules_passed:
                st.error("🛑 RULE VIOLATION DETECTED! You cannot submit a trade into this journal without satisfying all strategy checklists items first.")
            else:
                new_row = {
                    "Date": str(trade_date), "Pair": pair, "Direction": direction,
                    "Entry": entry_p, "SL": sl_p, "TP": tp_p, "P&L": pl_val,
                    "Status": status, "Reason": reason
                }
                st.session_state.trades = pd.concat([st.session_state.trades, pd.DataFrame([new_row])], ignore_index=True)
                st.success("🎯 Trade logged securely in your local database!")


# 5. CUSTOM RULES TEMPLATES
elif menu == "My Rules Templates":
    st.title("🛡️ Trading Rules & Discipline Strategy")
    st.write("Modify the core rules check criteria required by your setup layout.")
    
    new_rule = st.text_input("Add a core operational rule:")
    if st.button("Add Strategy Rule") and new_rule:
        st.session_state.rules.append(new_rule)
        st.success("New operational rule saved!")
        
    st.write("### Current Active Rules:")
    for idx, rule in enumerate(st.session_state.rules):
        st.write(f"**{idx+1}.** {rule}")