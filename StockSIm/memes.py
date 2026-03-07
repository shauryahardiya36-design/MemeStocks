import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime

# --- 1. CONFIGURATION ---
MARKET_FILE = "market_state.json"
USER_FILE = "users.json"
ADMIN_USER = "Mr. Shaurya Hardiya"
ADMIN_PASS = "ShauryaBoomBoom"

STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "base_cap": 1000000.0},
    "Sunny AI": {"price": 150.0, "base_cap": 1000000.0},
    "GCBROS": {"price": 50.0, "base_cap": 1000000.0}
}

# --- 2. DATA PERSISTENCE ---
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
        "emergency_last_used": 0,
        "bull_active_until": 0,
        "bull_last_month": 0
    })
    
    now = time.time()
    is_emergency = now < market.get("emergency_active_until", 0)
    is_bull = now < market.get("bull_active_until", 0)

    if now - market["last_update"] >= 10:
        current_month = datetime.now().month
        
        # --- RANDOM BULL RUN LOGIC (1% Chance) ---
        if not is_bull and not is_emergency and market.get("bull_last_month") != current_month:
            if random.random() < 0.01: 
                market["bull_active_until"] = now + (5 * 86400) # 5 Days
                market["bull_last_month"] = current_month
                is_bull = True
                for name in market["prices"]:
                    market["prices"][name] *= 1.25 # Instant 25% pump
                market["news"] = {"text": "🚀 UNKNOWN SIGNAL: A GLOBAL BULL RUN HAS BEGUN! +25% GAINS DETECTED.", "impact": {}}

        # Price Movement Calculation
        current_impacts = market["news"].get("impact", {})
        for name in market["prices"]:
            boost = current_impacts.get(name, 0)
            if is_bull:
                move = np.random.normal(0.0012, 0.001) 
            else:
                vol = 0.004 if is_emergency else 0.0018
                move = np.random.normal(0.0001 + boost, vol)
            market["prices"][name] *= (1 + move)
            
        market["history"].append(market["prices"].copy())
        if len(market["history"]) > 60: market["history"].pop(0)
        
        # Update News Wire
        if random.random() < 0.30:
            if is_emergency:
                market["news"] = {"text": "🚨 EMERGENCY: HARDIYA PROTOCOL ACTIVE.", "impact": {}}
            elif is_bull:
                market["news"] = {"text": "📈 BULL RUN: Optimism is high! Prices are pumping.", "impact": {}}
            else:
                market["news"] = {"text": "💬 GC chatter: New screenshots surfacing...", "impact": {}}
        
        market["last_update"] = now
        save_json(MARKET_FILE, market)
    
    return market, is_emergency, is_bull

# --- 3. UI SETUP ---
st.set_page_config(page_title="Shaurya Terminal", layout="wide")
market_state, is_emergency, is_bull = update_market_logic()
prices = market_state["prices"]

# Dynamic Themes
if is_emergency:
    st.markdown("<style>.stApp { background-color: #2b0505; }</style>", unsafe_allow_html=True)
elif is_bull:
    st.markdown("<style>.stApp { background-color: #051a05; }</style>", unsafe_allow_html=True)

# --- 4. MAIN DASHBOARD ---
status_txt = "🔴 EMERGENCY" if is_emergency else ("🚀 BULL RUN" if is_bull else "🟢 ONLINE")
st.title(f"🏛️ SHAURYA TERMINAL - {status_txt}")
st.info(f"🛰️ **WIRE:** {market_state['news']['text']}")

cols = st.columns(3)
for i, name in enumerate(prices):
    with cols[i]:
        hist = market_state["history"]
        delta = 0
        if len(hist) > 1:
            prev = hist[-2][name]
            delta = ((prices[name] - prev) / prev) * 100
        st.metric(name, f"${prices[name]:,.2f}", f"{delta:.3f}%")
        orig = STARTING_CONFIG[name]["price"]
        v_cap = (prices[name] / orig) * STARTING_CONFIG[name]["base_cap"]
        st.write(f"Valuation: **${v_cap:,.2f}**")

st.line_chart(pd.DataFrame(market_state["history"]), height=250)

# --- 5. SIDEBAR ---
st.sidebar.title("💳 TRADER AUTH")
users = load_json(USER_FILE, {})

if 'user' not in st.session_state:
    u_input = st.sidebar.text_input("Trader ID")
    pwd_input = ""
    if u_input == ADMIN_USER:
        pwd_input = st.sidebar.text_input("Admin Password", type="password")
    if st.sidebar.button("Connect"):
        if u_input == ADMIN_USER and pwd_input == ADMIN_PASS:
            st.session_state.user = u_input
            st.rerun()
        elif u_input and u_input != ADMIN_USER:
            if u_input not in users:
                users[u_input] = {"balance": 100000.0, "portfolio": {n: 0 for n in STARTING_CONFIG}}
                save_json(USER_FILE, users)
            st.session_state.user = u_input
            st.rerun()
else:
    users = load_json(USER_FILE, {})
    curr = st.session_state.user
    u_data = users[curr]
    st.sidebar.success(f"ONLINE: {curr}")
    
    st.sidebar.divider()
    st.sidebar.subheader("📦 Your Holdings")
    for n in STARTING_CONFIG:
        st.sidebar.write(f"{n}: **{u_data['portfolio'].get(n, 0)} shares**")
    
    p_val = sum(u_data["portfolio"].get(n, 0) * prices[n] for n in STARTING_CONFIG)
    st.sidebar.metric("Net Worth", f"${u_data['balance'] + p_val:,.2f}")
    st.sidebar.write(f"Cash: `${u_data['balance']:,.2f}`")

    # ADMIN GOD MODE
    if curr == ADMIN_USER:
        st.sidebar.divider()
        st.sidebar.subheader("👑 ADMIN POWERS")
        last_e = datetime.fromtimestamp(market_state.get("emergency_last_used", 0))
        can_e = (datetime.now().month != last_e.month) or (datetime.now().year != last_e.year)
        
        if st.sidebar.button("🚨 TRIGGER EMERGENCY", disabled=not can_e):
            for n in market_state["prices"]:
                market_state["prices"][n] *= (0.8 if n == "Shaurya Inc" else 0.6)
            market_state["emergency_active_until"] = time.time() + (4 * 86400)
            market_state["emergency_last_used"] = time.time()
            save_json(MARKET_FILE, market_state)
            st.rerun()

    # TRADING
    st.sidebar.divider()
    asset = st.sidebar.selectbox("Trade Asset", list(STARTING_CONFIG.keys()))
    amt = st.sidebar.number_input("Amount", min_value=0, step=1)
    b_col, s_col = st.sidebar.columns(2)
    
    if b_col.button("BUY"):
        cost = amt * prices[asset]
        if amt > 0 and u_data["balance"] >= cost:
            users[curr]["balance"] -= cost
            users[curr]["portfolio"][asset] = users[curr]["portfolio"].get(asset, 0) + amt
            save_json(USER_FILE, users)
            st.rerun()
    if s_col.button("SELL"):
        if amt > 0 and u_data["portfolio"].get(asset, 0) >= amt:
            users[curr]["balance"] += (amt * prices[asset])
            users[curr]["portfolio"][asset] -= amt
            save_json(USER_FILE, users)
            st.rerun()

    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.rerun()

# --- 6. LEADERBOARD ---
st.divider()
st.subheader("🏆 Leaderboard")
leaders = [{"Trader": uid, "Net Worth": d["balance"] + sum(d["portfolio"].get(n, 0) * prices[n] for n in STARTING_CONFIG)} for uid, d in users.items()]
st.dataframe(pd.DataFrame(leaders).sort_values("Net Worth", ascending=False), use_container_width=True, hide_index=True)

# --- 7. REFRESH ---
time.sleep(10)
st.rerun()