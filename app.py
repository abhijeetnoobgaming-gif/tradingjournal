import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="TradeDiary Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Professional UI Overrides */
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 2rem;}
    div.stButton > button {width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white;}
    .metric-card {background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #eee;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA PERSISTENCE ---
if 'trades' not in st.session_state:
    # Initial Dummy Data
    st.session_state.trades = pd.DataFrame([
        {'Date': '2023-10-01', 'Symbol': 'RELIANCE', 'Type': 'BUY', 'Qty': 10, 'Entry': 2400, 'Exit': 2450, 'PnL': 500, 'Charges': 20},
        {'Date': '2023-10-02', 'Symbol': 'NIFTY', 'Type': 'SELL', 'Qty': 50, 'Entry': 19800, 'Exit': 19750, 'PnL': 2500, 'Charges': 150}
    ])

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>TradeDiary Pro</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("MAIN MENU", ["📊 Dashboard", "📓 Trading Journal", "📅 Calendar", "⚙️ Settings"])
    st.spacer = st.markdown("<br>"*10, unsafe_allow_html=True)
    if st.button("➕ Add New Trade"):
        st.session_state.show_modal = True

# --- 4. CALCULATION ENGINE ---
df = pd.DataFrame(st.session_state.trades)
df['Date'] = pd.to_datetime(df['Date'])
total_pnl = df['PnL'].sum()
total_charges = df['Charges'].sum()
net_pnl = total_pnl - total_charges
win_rate = (len(df[df['PnL'] > 0]) / len(df) * 100) if not df.empty else 0

# --- 5. DASHBOARD PAGE ---
if menu == "📊 Dashboard":
    st.title("Performance Overview")
    
    # Top Row Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross PnL", f"₹{total_pnl:,.2f}")
    m2.metric("Charges", f"₹{total_charges:,.2f}")
    m3.metric("Net PnL", f"₹{net_pnl:,.2f}", delta_color="normal")
    m4.metric("Win Rate", f"{win_rate:.1f}%")

    # Charts
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Equity Curve (Net)")
        df_sorted = df.sort_values('Date')
        df_sorted['CumPnL'] = (df_sorted['PnL'] - df_sorted['Charges']).cumsum()
        fig = px.area(df_sorted, x='Date', y='CumPnL', color_discrete_sequence=['#1E3A8A'])
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Win vs Loss")
        fig2 = px.pie(values=[len(df[df['PnL']>0]), len(df[df['PnL']<=0])], names=['Wins', 'Losses'], color_discrete_sequence=['#10B981', '#EF4444'], hole=0.5)
        st.plotly_chart(fig2, use_container_width=True)

# --- 6. JOURNAL PAGE ---
elif menu == "📓 Trading Journal":
    st.title("Trade Logs")
    
    with st.expander("➕ Click to Log a New Trade"):
        with st.form("trade_form", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            t_date = f1.date_input("Date", date.today())
            t_sym = f2.text_input("Symbol", "SBIN")
            t_type = f3.selectbox("Type", ["BUY", "SELL"])
            
            f4, f5, f6 = st.columns(3)
            t_qty = f4.number_input("Quantity", min_value=1)
            t_entry = f5.number_input("Entry Price")
            t_exit = f6.number_input("Exit Price")
            
            t_charges = st.number_input("Brokerage/Charges", value=20.0)
            
            if st.form_submit_button("Save Trade"):
                pnl = (t_exit - t_entry) * t_qty if t_type == "BUY" else (t_entry - t_exit) * t_qty
                new_data = {'Date': str(t_date), 'Symbol': t_sym.upper(), 'Type': t_type, 
                            'Qty': t_qty, 'Entry': t_entry, 'Exit': t_exit, 'PnL': pnl, 'Charges': t_charges}
                st.session_state.trades = pd.concat([st.session_state.trades, pd.DataFrame([new_data])], ignore_index=True)
                st.rerun()

    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)

# --- 7. CALENDAR PAGE ---
elif menu == "📅 Calendar":
    st.title("PnL Calendar")
    st.info("Daily PnL heatmap based on trade exits.")
    
    # Simple Daily Aggregation
    daily_df = df.groupby('Date').agg({'PnL': 'sum', 'Charges': 'sum'}).reset_index()
    daily_df['Net'] = daily_df['PnL'] - daily_df['Charges']
    
    # Create a simple table calendar view
    daily_df['Date'] = daily_df['Date'].dt.date
    st.table(daily_df.style.applymap(lambda x: 'color: green' if x > 0 else 'color: red', subset=['Net']))

# --- 8. FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("TradeDiary Pro v1.0")
