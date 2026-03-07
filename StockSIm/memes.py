import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# --- 1. SETTINGS & CONSTANTS ---
MARKET_FILE = "market_state.json"
USER_FILE = "users.json"
ADMIN_USER = "Mr. Shaurya Hardiya"
ADMIN_PASS = "ShauryaBoomBoom"

STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "proxy": "Nvidia", "base_cap": 1000000.0},
    "Sunny AI": {"price": 150.0, "proxy": "Google", "base_cap": 1000000.0},
    "GCBROS": {"price": 50.0, "proxy": "Microsoft", "base_cap": 1000000.0}
}

# --- 2. CORE DATA FUNCTIONS ---
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as r: return json.load(r)
        except: return default
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def update_market_logic():
    market = load_json(MARKET_FILE, {
        "prices": {n: STARTING_CONFIG[n]["price"] for n in STARTING_CONFIG},
        "history": [],
        "news": {"text": "SYSTEM ONLINE", "impact": {}},
        "last_update": 0,
        "emergency_active_until": 0,
        "emergency_last_used": 0
    })
    
    now = time.time()
    is_emergency = now < market.get("emergency_active_until", 0)

    if now - market["last_update"] >= 10:
        current_impacts = market["news"].get("impact", {})
        for name in market["prices"]:
            boost = current_impacts.get(name, 0)
            vol = 0.004 if is_emergency else 0.0015
            move = np.random.normal(0.0001 + boost, vol)
            market["prices"][name] *= (1 + move)
            
        market["history"].append(market["prices"].copy())
        if len(market["history"]) > 60: market["history"].pop(0)
        
        if random.random() < 0.30:
            if is_emergency:
                market["news"] = {"text": "🚨 EMERGENCY: HARDIYA PROTOCOL ACTIVE.", "impact": {}}
            else:
                market["news"] = {"text": "💬 GC chatter: New screenshots surfacing...", "impact": {}}
        
        market["last_update"] = now
        save_json(MARKET_FILE, market)
    
    return market, is_emergency

# --- 3. UI SETUP ---
st.set_page_config(page_title="Shaurya Terminal", layout="wide")
market_state, is_emergency = update_market_logic()
prices = market_state["prices"]

# --- 4. MAIN DASHBOARD ---
st.title(f"🏛️ SHAURYA TERMINAL {'[RED ALERT]' if is_emergency else ''}")
st.info(f"🛰️ **WIRE:** {market_state['news']['text']}")

cols = st.columns(3)
for i, name in enumerate(prices):
    with cols[i]:
        # Calculate Delta
        hist = market_state["history"]
        delta = 0
        if len(hist) > 1:
            prev = hist[-2][name]
            delta = ((prices[name] - prev) / prev) * 100
        
        # Display Price Metric
        st.metric(name, f"${prices[name]:,.2f}", f"{delta:.3f}%")
        
        # --- NEW: VALUATION CALCULATION ---
        # Calculation: (Current Price / Starting Price) * Base Cap
        original_price = STARTING_CONFIG[name]["price"]
        current_cap = (prices[name] / original_price) * STARTING_CONFIG[name]["base_cap"]
        st.write(f"Valuation: **${current_cap:,.2f}**")

if market_state["history"]:
    st.line_chart(pd.DataFrame(market_state["history"]), height=250)

# --- 5. SIDEBAR: THE TRADING ENGINE ---
st.sidebar.title("💳 USER TERMINAL")
users = load_json(USER_FILE, {})

if 'user' not in st.session_state:
    user_input = st.sidebar.text_input("Enter Trader ID")
    pwd_input = ""
    if user_input == ADMIN_USER:
        pwd_input = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Connect"):
        if user_input == ADMIN_USER and pwd_input == ADMIN_PASS:
            st.session_state.user = user_input
            st.rerun()
        elif user_input and user_input != ADMIN_USER:
            if user_input not in users:
                users[user_input] = {"balance": 100000.0, "portfolio": {n: 0 for n in STARTING_CONFIG}}
                save_json(USER_FILE, users)
            st.session_state.user = user_input
            st.rerun()
        else:
            st.sidebar.error("Invalid Login")
else:
    users = load_json(USER_FILE, {})
    current_user = st.session_state.user
    u_data = users[current_user]
    
    st.sidebar.success(f"User: {current_user}")
    
    # CALCULATE NET WORTH
    total_port_value = sum(u_data["portfolio"].get(n, 0) * prices[n] for n in STARTING_CONFIG)
    st.sidebar.metric("Net Worth", f"${u_data['balance'] + total_port_value:,.2f}")
    st.sidebar.write(f"Available Cash: `${u_data['balance']:,.2f}`")

    # --- NEW: PORTFOLIO BREAKDOWN ---
    st.sidebar.divider()
    st.sidebar.subheader("📦 Your Holdings")
    for name in STARTING_CONFIG:
        qty = u_data["portfolio"].get(name, 0)
        st.sidebar.write(f"{name}: **{qty} shares**")

    # ADMIN PANEL
    if current_user == ADMIN_USER:
        st.sidebar.divider()
        if st.sidebar.button("🚨 TRIGGER EMERGENCY"):
            market_state["emergency_active_until"] = time.time() + (4 * 86400)
            for n in market_state["prices"]:
                market_state["prices"][n] *= (0.8 if n == "Shaurya Inc" else 0.6)
            save_json(MARKET_FILE, market_state)
            st.rerun()

    # TRADING SECTION
    st.sidebar.divider()
    asset = st.sidebar.selectbox("Select Asset to Trade", list(STARTING_CONFIG.keys()))
    qty_input = st.sidebar.number_input("Quantity", min_value=0, step=1, value=0)
    
    b_col, s_col = st.sidebar.columns(2)
    
    if b_col.button("BUY"):
        cost = qty_input * prices[asset]
        if qty_input > 0 and u_data["balance"] >= cost:
            users[current_user]["balance"] -= cost
            users[current_user]["portfolio"][asset] = users[current_user]["portfolio"].get(asset, 0) + qty_input
            save_json(USER_FILE, users)
            st.toast(f"Bought {qty_input} {asset}")
            time.sleep(0.5)
            st.rerun()
        else:
            st.sidebar.error("Trade Failed")

    if s_col.button("SELL"):
        if qty_input > 0 and u_data["portfolio"].get(asset, 0) >= qty_input:
            users[current_user]["balance"] += (qty_input * prices[asset])
            users[current_user]["portfolio"][asset] -= qty_input
            save_json(USER_FILE, users)
            st.toast(f"Sold {qty_input} {asset}")
            time.sleep(0.5)
            st.rerun()
        else:
            st.sidebar.error("Trade Failed")

    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.rerun()

# --- 6. THE HEARTBEAT ---
time.sleep(5)
st.rerun()