import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random

# --- 1. CONFIGURATION ---
MARKET_FILE = "market_state.json"
USER_FILE = "users.json"
STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "proxy": "Nvidia", "base_cap": 1000000.0},
    "Sunny AI": {"price": 150.0, "proxy": "Google", "base_cap": 1000000.0},
    "GCBROS": {"price": 50.0, "proxy": "Microsoft", "base_cap": 1000000.0}
}

NEWS_POOL = [
    {"text": "💎 Shaurya Inc. facilitates a 1-of-1 'Golden Screenshot' trade for $1.2M.", "impact": {"Shaurya Inc": 0.02}},
    {"text": "🚨 GCBROS CEO controversy causes market ripples.", "impact": {"GCBROS": -0.03}},
    {"text": "🎨 Sunny AI parody images of GCBROS go viral.", "impact": {"Sunny AI": 0.015, "GCBROS": -0.01}},
    {"text": "🚀 Shaurya Inc (NVDA) inventory surge reported.", "impact": {"Shaurya Inc": 0.03}}
]

# --- 2. SHARED DATA UTILITIES ---
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return default
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def get_synced_market():
    """Syncs market prices across all users using a shared JSON file."""
    market = load_json(MARKET_FILE, {
        "prices": {n: STARTING_CONFIG[n]["price"] for n in STARTING_CONFIG},
        "history": [],
        "news": {"text": "SYSTEM ONLINE", "impact": {}},
        "last_update": 0
    })
    
    now = time.time()
    # Only update prices if 10 seconds have passed globally
    if now - market["last_update"] >= 10:
        current_impacts = market["news"].get("impact", {})
        
        for name in market["prices"]:
            boost = current_impacts.get(name, 0)
            move = np.random.normal(0.0001 + boost, 0.001)
            market["prices"][name] *= (1 + move)
        
        # Log history
        market["history"].append(market["prices"].copy())
        if len(market["history"]) > 50: market["history"].pop(0)
        
        # Update News
        if random.random() < 0.20:
            market["news"] = random.choice(NEWS_POOL)
        else:
            market["news"]["impact"] = {k: v*0.5 for k, v in market["news"].get("impact", {}).items()}
            
        market["last_update"] = now
        save_json(MARKET_FILE, market)
    
    return market

# --- 3. UI INITIALIZATION ---
st.set_page_config(page_title="Shaurya Terminal", layout="wide")
st.markdown("""<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #2d2f39; }
    .stInfo { background-color: #002b36; border-left: 5px solid #268bd2; font-family: monospace; }
</style>""", unsafe_allow_html=True)

# 4. FETCH GLOBAL DATA
market_state = get_synced_market()
prices = market_state["prices"]

# --- 5. MAIN TERMINAL ---
st.markdown("### 🏛️ SHAURYA INC. GLOBAL REAL-TIME TERMINAL")
st.info(f"🛰️ **WIRE:** {market_state['news']['text']}")

m_cols = st.columns(3)
for i, name in enumerate(prices):
    with m_cols[i]:
        # Calculate Delta from history
        delta_pct = 0
        if len(market_state["history"]) > 1:
            prev = market_state["history"][-2][name]
            delta_pct = ((prices[name] - prev) / prev) * 100
            
        st.metric(label=f"{name} ({STARTING_CONFIG[name]['proxy']})", 
                  value=f"${prices[name]:,.2f}", 
                  delta=f"{delta_pct:.3f}%")
        
        original_p = STARTING_CONFIG[name]["price"]
        cap = (prices[name] / original_p) * 1000000.0
        st.write(f"Valuation: **${cap:,.2f}**")

# Charting
if market_state["history"]:
    st.line_chart(pd.DataFrame(market_state["history"]), height=300)

# --- 6. SIDEBAR: PERSONAL ACCOUNT ---
st.sidebar.title("💳 TRADER AUTH")
users = load_json(USER_FILE, {})

if 'user' not in st.session_state:
    user_id = st.sidebar.text_input("Trader ID", placeholder="Enter Username...")
    if st.sidebar.button("Connect"):
        if user_id:
            if user_id not in users:
                users[user_id] = {"balance": 100000.0, "portfolio": {n: 0 for n in STARTING_CONFIG}}
                save_json(USER_FILE, users)
            st.session_state.user = user_id
            st.rerun()
else:
    u = users[st.session_state.user]
    port_val = sum(u["portfolio"][n] * prices[n] for n in STARTING_CONFIG)
    net_worth = u["balance"] + port_val
    
    st.sidebar.success(f"ONLINE: {st.session_state.user}")
    st.sidebar.metric("Net Worth", f"${net_worth:,.2f}", delta=f"{(net_worth - 100000):,.2f}")
    st.sidebar.write(f"Cash: `${u['balance']:,.2f}`")
    
    st.sidebar.divider()
    tgt = st.sidebar.selectbox("Select Asset", list(STARTING_CONFIG.keys()))
    amt = st.sidebar.number_input("Quantity", min_value=0, step=1)
    
    b, s = st.sidebar.columns(2)
    if b.button("BUY", use_container_width=True):
        cost = amt * prices[tgt]
        if u["balance"] >= cost and amt > 0:
            u["balance"] -= cost
            u["portfolio"][tgt] += amt
            save_json(USER_FILE, users)
            st.toast(f"Purchased {amt} of {tgt}")
            st.rerun()
        else: st.sidebar.error("Insufficient Funds")

    if s.button("SELL", use_container_width=True):
        if u["portfolio"][tgt] >= amt and amt > 0:
            u["balance"] += (amt * prices[tgt])
            u["portfolio"][tgt] -= amt
            save_json(USER_FILE, users)
            st.toast(f"Liquidated {amt} of {tgt}")
            st.rerun()
        else: st.sidebar.error("Insufficient Shares")

# 7. REFRESH
time.sleep(10)
st.rerun()