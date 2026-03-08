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
            with open(file, "r") as r: return json.load(r)
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
        last_act = datetime.fromisoformat(d.get("last_action", now.isoformat()))
        if (now - last_act).total_seconds() > (72 * 3600):
            days_stagnant = (now - last_act).total_seconds() / 86400
            decay = d["balance"] * (0.02 * days_stagnant)
            users[uid]["balance"] -= decay
            users[uid]["last_action"] = now.isoformat() # Reset clock after taxing
            updated = True
    
    if updated: save_json(USER_FILE, users)
    return users

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
        
        if not is_bull and not is_emergency and market.get("bull_last_month") != current_month:
            if random.random() < 0.01: 
                market["bull_active_until"] = now + (5 * 86400)
                market["bull_last_month"] = current_month
                is_bull = True
                for name in market["prices"]:
                    market["prices"][name] *= 1.25
                market["news"] = {"text": "🚀 UNKNOWN SIGNAL: A GLOBAL BULL RUN HAS BEGUN! +25% GAINS DETECTED.", "impact": {}}

        current_impacts = market["news"].get("impact", {})
        for name in market["prices"]:
            boost = current_impacts.get(name, 0)
            if is_bull: move = np.random.normal(0.0012, 0.001) 
            else:
                vol = 0.004 if is_emergency else 0.0018
                move = np.random.normal(0.0001 + boost, vol)
            market["prices"][name] *= (1 + move)
            
        market["history"].append(market["prices"].copy())
        if len(market["history"]) > 60: market["history"].pop(0)
        
        if random.random() < 0.30:
            if is_emergency: market["news"] = {"text": "🚨 EMERGENCY: HARDIYA PROTOCOL ACTIVE.", "impact": {}}
            elif is_bull: market["news"] = {"text": "📈 BULL RUN: Optimism is high! Prices are pumping.", "impact": {}}
            else: market["news"] = {"text": "💬 GC chatter: New screenshots surfacing...", "impact": {}}
        
        market["last_update"] = now
        save_json(MARKET_FILE, market)
    
    return market, is_emergency, is_bull

# --- 4. UI SETUP ---
st.set_page_config(page_title="Memeconomy Trading Platform", layout="wide")
market_state, is_emergency, is_bull = update_market_logic()
prices = market_state["prices"]
users = load_json(USER_FILE, {})
users = apply_system_rules(users)

if is_emergency: st.markdown("<style>.stApp { background-color: #2b0505; }</style>", unsafe_allow_html=True)
elif is_bull: st.markdown("<style>.stApp { background-color: #051a05; }</style>", unsafe_allow_html=True)

# --- 5. MAIN DASHBOARD ---
status_txt = "🔴 EMERGENCY" if is_emergency else ("🚀 BULL RUN" if is_bull else "🟢 ONLINE")
st.title(f"🏛️ Memeconomy Trading Platform - {status_txt}")
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

# --- 6. SIDEBAR & AUTH ---
st.sidebar.title("💳 TRADER AUTH")

if 'user' not in st.session_state:
    u_input = st.sidebar.text_input("Trader ID")
    pwd_input = st.sidebar.text_input("Admin Password", type="password") if u_input == ADMIN_USER else ""
    if st.sidebar.button("Connect"):
        if u_input == ADMIN_USER and pwd_input == ADMIN_PASS:
            st.session_state.user = u_input
            st.rerun()
        elif u_input and u_input != ADMIN_USER:
            # IDENTITY PROTECTION: Prevent hijacking CEO name
            if u_input.strip() == ADMIN_USER:
                st.sidebar.error("Sovereign Identity Protection: Name Reserved.")
            else:
                if u_input not in users:
                    users[u_input] = {
                        "balance": 100000.0, 
                        "portfolio": {n: 0 for n in STARTING_CONFIG},
                        "last_action": datetime.now().isoformat(),
                        "is_ghosted": False,
                        "is_kitten": False
                    }
                    save_json(USER_FILE, users)
                st.session_state.user = u_input
                st.rerun()
else:
    curr = st.session_state.user
    
    # 6.1 CEO AUTH BYPASS (Prevent KeyError)
    if curr == ADMIN_USER:
        u_data = {
            "balance": 999999999.0, 
            "portfolio": {n: 0 for n in STARTING_CONFIG},
            "is_ghosted": False,
            "is_kitten": False
        }
    else:
        u_data = users[curr]
    
    # Ghosting Protocol (Article 4.1.1)
    display_balance = u_data['balance'] / 100 if u_data.get("is_ghosted") else u_data['balance']
    
    st.sidebar.success(f"ONLINE: {curr}")
    if u_data.get("is_kitten"): st.sidebar.warning("🐱 STATUS: ROBLOX KITTEN")
    
    st.sidebar.divider()
    st.sidebar.subheader("📦 Your Holdings")
    for n in STARTING_CONFIG:
        st.sidebar.write(f"{n}: **{u_data['portfolio'].get(n, 0)} shares**")
    
    p_val = sum(u_data["portfolio"].get(n, 0) * prices[n] for n in STARTING_CONFIG)
    st.sidebar.metric("Net Worth", f"${display_balance + p_val:,.2f}")
    st.sidebar.write(f"Cash: `${display_balance:,.2f}`")

    # 7. ADMIN GOD MODE (SHAURYA ONLY)
    if curr == ADMIN_USER:
        st.sidebar.divider()
        with st.sidebar.expander("👑 CEO CONTROL PANEL"):
            # Emergency Trigger
            last_e = datetime.fromtimestamp(market_state.get("emergency_last_used", 0))
            can_e = (datetime.now().month != last_e.month) or (datetime.now().year != last_e.year)
            if st.button("🚨 TRIGGER EMERGENCY", disabled=not can_e):
                for n in market_state["prices"]:
                    market_state["prices"][n] *= (0.8 if n == "Shaurya Inc" else 0.6)
                market_state["emergency_active_until"] = time.time() + (4 * 86400)
                market_state["emergency_last_used"] = time.time()
                save_json(MARKET_FILE, market_state)
                st.rerun()

            # Audit & Tax (Article 4.2 & 6.2)
            st.divider()
            target = st.selectbox("Select Target", [u for u in users if u != ADMIN_USER])
            tax_amt = st.number_input("Tax Amount ($)", min_value=0.0)
            if st.button("Levy Salt/Insolence Tax"):
                users[target]["balance"] -= tax_amt
                save_json(USER_FILE, users)
                st.toast(f"Tax levied on {target}")

    # 8. TRADING
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

# --- 10. REFRESH ---
time.sleep(10)
st.rerun()