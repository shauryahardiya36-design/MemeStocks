import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

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
            with open(file, "r") as r:
                content = r.read().strip()
                if not content: return default
                return json.loads(content)
        except: return default
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --- 3. SYSTEM LOGIC (DECAY & SAFETY) ---
def apply_system_rules(users):
    now = datetime.now()
    updated = False
    for uid, d in users.items():
        if uid == ADMIN_USER: continue
        
        # 3.1 Sovereign Safety Net (Article 5.7)
        if d.get("balance", 0) < 1000:
            users[uid]["balance"] = 1000.0
            updated = True
            
        # 3.2 Stagnation Decay (Article 4.3)
        last_act_str = d.get("last_action")
        if last_act_str:
            last_act = datetime.fromisoformat(last_act_str)
            if (now - last_act).total_seconds() > (72 * 3600):
                days_stagnant = (now - last_act).total_seconds() / 86400
                decay = d["balance"] * (0.02 * days_stagnant)
                users[uid]["balance"] -= decay
                users[uid]["last_action"] = now.isoformat()
                updated = True
    
    if updated: save_json(USER_FILE, users)
    return users

def update_market_logic():
    # 1. Load state - Strictly avoid defaulting to STARTING_CONFIG if file exists
    market = load_json(MARKET_FILE, None)
    
    if market is None or "prices" not in market:
        market = {
            "prices": {n: STARTING_CONFIG[n]["price"] for n in STARTING_CONFIG},
            "history": [],
            "news": {"text": "SYSTEM INITIALIZED", "impact": {}},
            "last_update": 0,
            "emergency_active_until": 0,
            "emergency_last_used": 0,
            "bull_active_until": 0,
            "bull_last_month": 0
        }
    
    now = time.time()
    is_emergency = now < market.get("emergency_active_until", 0)
    is_bull = now < market.get("bull_active_until", 0)

    # 2. Market Pulse (Every 10 seconds)
    if now - market["last_update"] >= 10:
        current_month = datetime.now().month
        
        # Random Bull Run Trigger (1% chance per pulse if not active)
        if not is_bull and not is_emergency and market.get("bull_last_month") != current_month:
            if random.random() < 0.01: 
                market["bull_active_until"] = now + (5 * 86400) # 5 Day Duration
                market["bull_last_month"] = current_month
                is_bull = True
                for name in market["prices"]:
                    market["prices"][name] *= 1.25 # Instant 25% Pump
                market["news"] = {"text": "🚀 GLOBAL BULL RUN DETECTED! Markets surging.", "impact": {}}

        # Price Evolution Logic
        for name in market["prices"]:
            if is_bull:
                move = np.random.normal(0.0018, 0.0012) # Strong Growth
            elif is_emergency:
                move = np.random.normal(-0.0025, 0.004) # Rapid Decay
            else:
                move = np.random.normal(0.0001, 0.0018) # Normal Volatility
            
            market["prices"][name] *= (1 + move)
            
        # Update History
        market["history"].append(market["prices"].copy())
        if len(market["history"]) > 60: market["history"].pop(0)
        
        # Sticky News Logic
        if is_bull: market["news"]["text"] = "🚀 BULL RUN: Optimism is at an all-time high."
        elif is_emergency: market["news"]["text"] = "🚨 EMERGENCY: Hardiya Protocol enforcing correction."
        elif random.random() < 0.1:
            market["news"]["text"] = random.choice(["💬 GC chatter: New screenshots surfacing...", "📈 Market showing stable resistance.", "🔍 Analysts predict a volatile week."])
        
        market["last_update"] = now
        save_json(MARKET_FILE, market)
    
    return market, is_emergency, is_bull

# --- 4. UI SETUP ---
st.set_page_config(page_title="Memeconomy Terminal", layout="wide")
market_state, is_emergency, is_bull = update_market_logic()
prices = market_state["prices"]
users = load_json(USER_FILE, {})
users = apply_system_rules(users)

# Dynamic Theming
if is_emergency: st.markdown("<style>.stApp { background-color: #2b0505; }</style>", unsafe_allow_html=True)
elif is_bull: st.markdown("<style>.stApp { background-color: #051a05; }</style>", unsafe_allow_html=True)

# --- 5. MAIN DASHBOARD ---
status_txt = "🔴 EMERGENCY" if is_emergency else ("🚀 BULL RUN" if is_bull else "🟢 ONLINE")
st.title(f"🏛️ Shaurya Mainframe - {status_txt}")
st.info(f"🛰️ **WIRE:** {market_state['news']['text']}")

# Price Cards
cols = st.columns(3)
for i, name in enumerate(prices):
    with cols[i]:
        hist = market_state["history"]
        delta = 0
        if len(hist) > 1:
            prev = hist[-2][name]
            delta = ((prices[name] - prev) / prev) * 100
        st.metric(name, f"${prices[name]:,.2f}", f"{delta:.3f}%")
        
        # Valuation math
        orig = STARTING_CONFIG[name]["price"]
        v_cap = (prices[name] / orig) * STARTING_CONFIG[name]["base_cap"]
        st.write(f"Valuation: **${v_cap:,.2f}**")

st.line_chart(pd.DataFrame(market_state["history"]), height=250)

# --- 6. SIDEBAR & AUTH ---
st.sidebar.title("💳 TRADER AUTH")

if 'user' not in st.session_state:
    u_input = st.sidebar.text_input("Trader ID")
    pwd_input = st.sidebar.text_input("Admin Password", type="password") if u_input == ADMIN_USER else ""
    if st.sidebar.button("Connect"):
        if u_input == ADMIN_USER:
            if pwd_input == ADMIN_PASS:
                if ADMIN_USER not in users:
                    users[ADMIN_USER] = {"balance": 100000.0, "portfolio": {n: 0 for n in STARTING_CONFIG}, "last_action": datetime.now().isoformat(), "is_ghosted": False, "is_kitten": False}
                    save_json(USER_FILE, users)
                st.session_state.user = u_input
                st.rerun()
            else: st.sidebar.error("Invalid Admin Credentials")
        elif u_input:
            if u_input not in users:
                users[u_input] = {"balance": 100000.0, "portfolio": {n: 0 for n in STARTING_CONFIG}, "last_action": datetime.now().isoformat(), "is_ghosted": False, "is_kitten": False}
                save_json(USER_FILE, users)
            st.session_state.user = u_input
            st.rerun()
else:
    curr = st.session_state.user
    u_data = users[curr]
    
    # Ghosting check
    display_balance = u_data['balance'] / 100 if u_data.get("is_ghosted") else u_data['balance']
    
    st.sidebar.success(f"ONLINE: {curr}")
    if u_data.get("is_kitten"): st.sidebar.warning("🐱 STATUS: ROBLOX KITTEN")
    
    st.sidebar.divider()
    st.sidebar.subheader("📦 Holdings")
    for n in STARTING_CONFIG:
        st.sidebar.write(f"{n}: **{u_data['portfolio'].get(n, 0)}**")
    
    p_val = sum(u_data["portfolio"].get(n, 0) * prices[n] for n in STARTING_CONFIG)
    st.sidebar.metric("Net Worth", f"${display_balance + p_val:,.2f}")
    st.sidebar.write(f"Cash: `${display_balance:,.2f}`")

    # 7. CEO PANEL
    if curr == ADMIN_USER:
        st.sidebar.divider()
        with st.sidebar.expander("👑 CEO CONTROL"):
            # Emergency
            last_e = datetime.fromtimestamp(market_state.get("emergency_last_used", 0))
            can_e = (datetime.now().month != last_e.month) or (datetime.now().year != last_e.year)
            if st.button("🚨 TRIGGER EMERGENCY", disabled=not can_e):
                for n in market_state["prices"]:
                    market_state["prices"][n] *= 0.7
                market_state["emergency_active_until"] = time.time() + (4 * 86400)
                market_state["emergency_last_used"] = time.time()
                save_json(MARKET_FILE, market_state)
                st.rerun()
            
            # Manual Bull Run
            if st.button("🚀 FORCE BULL RUN"):
                market_state["bull_active_until"] = time.time() + (5 * 86400)
                for n in market_state["prices"]: market_state["prices"][n] *= 1.25
                save_json(MARKET_FILE, market_state)
                st.rerun()
                
            # Manual Stop Bull Run
            if is_bull:
                if st.button("🛑 TERMINATE BULL RUN"):
                    market_state["bull_active_until"] = 0
                    market_state["news"]["text"] = "📉 BULL RUN TERMINATED BY CEO MANDATE."
                    save_json(MARKET_FILE, market_state)
                    st.rerun()

            # Taxation
            st.divider()
            target = st.selectbox("Select Target", [u for u in users if u != ADMIN_USER])
            tax_amt = st.number_input("Tax ($)", min_value=0.0)
            if st.button("Levy Tax"):
                users[target]["balance"] -= tax_amt
                save_json(USER_FILE, users)
                st.toast(f"Tax levied on {target}")

    # 8. TRADING ENGINE
    st.sidebar.divider()
    asset = st.sidebar.selectbox("Trade Asset", list(STARTING_CONFIG.keys()))
    amt = st.sidebar.number_input("Amount", min_value=0, step=1)
    b_col, s_col = st.sidebar.columns(2)
    
    if b_col.button("BUY"):
        cost = amt * prices[asset]
        if amt > 0 and u_data["balance"] >= cost:
            users[curr]["balance"] -= cost
            users[curr]["portfolio"][asset] = users[curr]["portfolio"].get(asset, 0) + amt
            users[curr]["last_action"] = datetime.now().isoformat()
            save_json(USER_FILE, users)
            st.rerun()
            
    if s_col.button("SELL"):
        if amt > 0 and u_data["portfolio"].get(asset, 0) >= amt:
            users[curr]["balance"] += (amt * prices[asset])
            users[curr]["portfolio"][asset] -= amt
            users[curr]["last_action"] = datetime.now().isoformat()
            save_json(USER_FILE, users)
            st.rerun()

    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.rerun()

# 9. REFRESH
time.sleep(10)
st.rerun()