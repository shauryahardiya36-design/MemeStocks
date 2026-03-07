import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & CORE DATA ---
# Shaurya Inc (NVDA) | Sunny AI (GOOGL) | GCBROS (MSFT)
TICKERS = {
    "Shaurya Inc": {"p_start": 100.0, "proxy": "Nvidia", "cap_start": 1000000.0},
    "Sunny AI": {"p_start": 150.0, "proxy": "Google", "cap_start": 1000000.0},
    "GCBROS": {"p_start": 50.0, "proxy": "Microsoft", "cap_start": 1000000.0}
}

NEWS_POOL = [
    "💎 Shaurya Inc. secures a 'Legendary Holo' screenshot; meme liquidity hits $5M.",
    "🚨 GCBROS CEO issues a controversial late-night statement; volatility triples.",
    "🎨 Sunny AI releases a 'Deepfake GCBROS' video; parity traffic crashes servers.",
    "🚀 Shaurya Inc (NVDA) announces a 'Meme Dividend' for long-term holders.",
    "⚠️ GCBROS platform restricted in 5 regions following 'unfiltered' board meeting leak.",
    "🤖 Sunny AI's new generator creates a 'Boss Shaurya' AI avatar for the terminal."
]

# --- 2. DATA PERSISTENCE ---
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f: return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- 3. PAGE SETUP & UI ---
st.set_page_config(page_title="Shaurya Executive Terminal", layout="wide")

# Dark-Mode Professional Styling
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .stInfo { background-color: #0d1117; border-left: 5px solid #238636; }
    .stHeader { font-family: 'Courier New', Courier, monospace; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'market' not in st.session_state:
    st.session_state.market = {n: {"p": v["p_start"], "c": v["cap_start"]} for n, v in TICKERS.items()}
    st.session_state.history = pd.DataFrame([{t: v["p_start"] for t, v in TICKERS.items()}])
    st.session_state.news = "TERMINAL ONLINE: Awaiting Executive Orders from Mr. Shaurya Hardiya."
    st.session_state.cooldowns = load_json("cooldowns.json", {t: 0 for t in TICKERS})

# --- 4. THE REAL-TIME ENGINE ---
main_placeholder = st.empty()

while True:
    with main_placeholder.container():
        st.markdown("<h1 class='stHeader'>🏛️ SHAURYA INC. GLOBAL EXECUTIVE TERMINAL</h1>", unsafe_allow_html=True)
        
        # Professional News Ticker
        st.info(f"🛰️ **WIRE:** {st.session_state.news}")
        
        # 5. MARKET TICKER ROW
        m_cols = st.columns(3)
        for i, (name, config) in enumerate(TICKERS.items()):
            # Natural Drift (Random Walk)
            drift = np.random.normal(0.0001, 0.0006)
            st.session_state.market[name]["p"] *= (1 + drift)
            
            # MATH: Market Cap is scaled proportionally from the $1M start
            # (Current Price / Starting Price) * $1,000,000
            st.session_state.market[name]["c"] = (st.session_state.market[name]["p"] / config["p_start"]) * 1000000.0
            
            with m_cols[i]:
                st.metric(label=f"{name} ({config['proxy']})", 
                          value=f"${st.session_state.market[name]['p']:.2f}", 
                          delta=f"{drift*100:.3f}%")
                st.caption(f"Market Cap: **${st.session_state.market[name]['c']:,.2f}**")

        # 6. LIVE PERFORMANCE CHART
        new_row = {t: st.session_state.market[t]["p"] for t in TICKERS}
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True).iloc[-50:]
        st.line_chart(st.session_state.history, height=300)

        # 7. SIDEBAR: ACCOUNT & ADMIN POWERS
        st.sidebar.title("🔐 ACCESS CONTROL")
        
        # --- ADMIN PANEL: MR. SHAURYA HARDIYA ---
        with st.sidebar.expander("👑 EXECUTIVE OVERRIDE"):
            admin_pass = st.text_input("Enter Admin Key", type="password")
            if admin_pass == "SHAURYA_BOSS":
                st.success("Authorized: Mr. Shaurya Hardiya")
                target = st.selectbox("Target Company", list(TICKERS.keys()))
                
                # Cooldown Check (7 Days)
                last_ts = st.session_state.cooldowns.get(target, 0)
                last_used = datetime.fromtimestamp(last_ts)
                ready_date = last_used + timedelta(days=7)
                
                if datetime.now() > ready_date:
                    shift = st.select_slider("Select Market Shock", options=[-0.30, -0.15, 0.15, 0.30])
                    if st.button("EXECUTE SHOCK"):
                        st.session_state.market[target]["p"] *= (1 + shift)
                        st.session_state.cooldowns[target] = datetime.now().timestamp()
                        save_json("cooldowns.json", st.session_state.cooldowns)
                        st.session_state.news = f"⚠️ EXECUTIVE SHOCK: {target} price shifted by {shift*100}% by order of Mr. Shaurya Hardiya."
                        st.rerun()
                else:
                    st.warning(f"Power Locked for {target}. Ready on {ready_date.strftime('%Y-%m-%d')}")

        # --- TRADER LOGIN ---
        st.sidebar.divider()
        users = load_json("users.json", {})
        if 'user' not in st.session_state:
            u_id = st.sidebar.text_input("Trader ID")
            if st.sidebar.button("Login"):
                if u_id not in users:
                    users[u_id] = {"bal": 100000.0, "port": {t: 0 for t in TICKERS}}
                    save_json("users.json", users)
                st.session_state.user = u_id
                st.rerun()
        else:
            u = users[st.session_state.user]
            st.sidebar.write(f"Logged in as: **{st.session_state.user}**")
            st.sidebar.metric("Balance", f"${u['bal']:,.2f}")
            
            # --- TRANSACTION ENGINE ---
            st.sidebar.subheader("⚡ Order Book")
            trade_tgt = st.sidebar.selectbox("Asset", list(TICKERS.keys()), key="trade_asset")
            price_now = st.session_state.market[trade_tgt]["p"]
            owned = u["port"].get(trade_tgt, 0)
            
            st.sidebar.write(f"Owned: `{owned}` shares")
            qty = st.sidebar.number_input("Shares", min_value=0, step=1)
            
            b_col, s_col = st.sidebar.columns(2)
            if b_col.button("BUY", use_container_width=True):
                if u["bal"] >= (qty * price_now) and qty > 0:
                    u["bal"] -= (qty * price_now)
                    u["port"][trade_tgt] += qty
                    save_json("users.json", users)
                    st.toast(f"Purchased {qty} {trade_tgt}")
                else: st.sidebar.error("Funds Low")

            if s_col.button("SELL", use_container_width=True):
                # EXPLOIT GUARD: Must own the shares
                if owned >= qty and qty > 0:
                    u["bal"] += (qty * price_now)
                    u["port"][trade_tgt] -= qty
                    save_json("users.json", users)
                    st.toast(f"Sold {qty} {trade_tgt}")
                else: st.sidebar.error("Exploit Blocked")

        # Cycle news 15% of the time
        if random.random() < 0.15:
            st.session_state.news = random.choice(NEWS_POOL)

        # THE PULSE: 30-second delay
        time.sleep(30)
        st.rerun()