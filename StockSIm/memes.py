import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random

# --- 1. MARKET ARCHITECTURE ---
STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "proxy": "Nvidia", "base_cap": 1000000.0},
    "Sunny AI": {"price": 150.0, "proxy": "Google", "base_cap": 1000000.0},
    "GCBROS": {"price": 50.0, "proxy": "Microsoft", "base_cap": 1000000.0}
}

NEWS_POOL = [
    {"text": "💎 Shaurya Inc. facilitates the trade of a 1-of-1 'Golden Screenshot' for $1.2M.", "impact": {"Shaurya Inc": 0.02}},
    {"text": "🚨 GCBROS CEO doubles down on controversial statements; volatility spikes.", "impact": {"GCBROS": -0.03}},
    {"text": "🎨 Sunny AI releases 'Candid GCBROS' photo pack; viral parody boost.", "impact": {"Sunny AI": 0.015, "GCBROS": -0.01}},
    {"text": "📦 Shaurya Inc. digitizes 4 petabytes of vintage group chat logs.", "impact": {"Shaurya Inc": 0.005}},
    {"text": "🎥 Sunny AI's new generator creates a 'Deepfake Shaurya' causing board confusion.", "impact": {"Sunny AI": 0.02, "Shaurya Inc": -0.01}},
    {"text": "⚠️ GCBROS platform restricted in 3 countries after midnight rant.", "impact": {"GCBROS": -0.05}},
    {"text": "🚀 Shaurya Inc (NVDA) inventory surge: 50,000 rare units moved.", "impact": {"Shaurya Inc": 0.03}}
]

# --- 2. DATA UTILITIES ---
def load_users():
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f: return json.load(f)
        except: return {}
    return {}

def save_users(users):
    with open("users.json", "w") as f: json.dump(users, f, indent=4)

# --- 3. UI INITIALIZATION ---
st.set_page_config(page_title="Shaurya Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #2d2f39; }
    .stInfo { background-color: #002b36; border-left: 5px solid #268bd2; color: #93a1a1; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

if 'market_data' not in st.session_state:
    st.session_state.market_data = {
        name: {"price": info["price"], "cap": info["base_cap"], "proxy": info["proxy"]} 
        for name, info in STARTING_CONFIG.items()
    }
    st.session_state.history = pd.DataFrame([{t: STARTING_CONFIG[t]["price"] for t in STARTING_CONFIG}])
    st.session_state.current_news = {"text": "SYSTEM ONLINE: Market initialized.", "impact": {}}

# --- 4. THE LIVE ENGINE ---
placeholder = st.empty()

# Main Loop
with placeholder.container():
    st.markdown("### 🏛️ SHAURYA INC. GLOBAL REAL-TIME TERMINAL")
    
    # Professional News Ribbon
    st.info(f"🛰️ **WIRE:** {st.session_state.current_news['text']}")
    
    # 5. LIVE MARKET METRICS
    m_cols = st.columns(3)
    current_impacts = st.session_state.current_news.get("impact", {})
    
    for i, (name, data) in enumerate(st.session_state.market_data.items()):
        news_boost = current_impacts.get(name, 0)
        move = np.random.normal(0.0001 + news_boost, 0.001)
        data["price"] *= (1 + move)
        
        original_p = STARTING_CONFIG[name]["price"]
        data["cap"] = (data["price"] / original_p) * 1000000.0
        
        with m_cols[i]:
            st.metric(label=f"{name} ({data['proxy']})", 
                      value=f"${data['price']:.2f}", 
                      delta=f"{move*100:.3f}%")
            st.write(f"Valuation: **${data['cap']:,.2f}**")

    # 6. PERFORMANCE CHART
    new_row = {t: st.session_state.market_data[t]["price"] for t in STARTING_CONFIG}
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True).iloc[-50:]
    st.line_chart(st.session_state.history, height=300)

    # 7. SIDEBAR: ACCOUNT & TRADING
    st.sidebar.title("💳 TRADER AUTH")
    users = load_users()
    
    if 'user' not in st.session_state:
        user_id = st.sidebar.text_input("Enter Trader ID", placeholder="Username...")
        if st.sidebar.button("Establish Connection"):
            if user_id:
                if user_id not in users:
                    users[user_id] = {"balance": 100000.0, "portfolio": {t: 0 for t in STARTING_CONFIG}}
                    save_users(users)
                st.session_state.user = user_id
                st.rerun()
    else:
        u = users[st.session_state.user]
        port_val = sum(u["portfolio"][t] * st.session_state.market_data[t]["price"] for t in STARTING_CONFIG)
        net_worth = u["balance"] + port_val
        
        st.sidebar.success(f"ONLINE: {st.session_state.user}")
        st.sidebar.metric("Net Worth", f"${net_worth:,.2f}", delta=f"{(net_worth - 100000):,.2f}")
        st.sidebar.write(f"Cash Available: `${u['balance']:,.2f}`")
        
        st.sidebar.divider()
        st.sidebar.subheader("⚡ Execute Order")
        tgt = st.sidebar.selectbox("Select Asset", list(STARTING_CONFIG.keys()))
        curr_p = st.session_state.market_data[tgt]["price"]
        owned = u["portfolio"].get(tgt, 0)
        
        st.sidebar.write(f"Currently Held: `{owned}` shares")
        amt = st.sidebar.number_input("Quantity", min_value=0, step=1, key="trade_amt")
        
        b_col, s_col = st.sidebar.columns(2)
        if b_col.button("BUY", use_container_width=True):
            cost = amt * curr_p
            if u["balance"] >= cost and amt > 0:
                u["balance"] -= cost
                u["portfolio"][tgt] += amt
                save_users(users)
                st.toast(f"Bought {amt} of {tgt}")
                time.sleep(1) # Give user time to see toast
                st.rerun()
            else: st.sidebar.error("Insufficient Funds")

        if s_col.button("SELL", use_container_width=True):
            if owned >= amt and amt > 0:
                u["balance"] += (amt * curr_p)
                u["portfolio"][tgt] -= amt
                save_users(users)
                st.toast(f"Sold {amt} of {tgt}")
                time.sleep(1)
                st.rerun()
            else: st.sidebar.error("Insufficient Shares")

    # 8. BACKGROUND LOGIC
    if random.random() < 0.20:
        st.session_state.current_news = random.choice(NEWS_POOL)
    else:
        # Decay news impact
        st.session_state.current_news["impact"] = {k: v*0.5 for k, v in st.session_state.current_news.get("impact", {}).items()}

# 9. REFRESH TIMER
time.sleep(10)
st.rerun()