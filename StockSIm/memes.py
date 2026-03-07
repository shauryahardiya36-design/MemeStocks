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
STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "proxy": "Nvidia"},
    "Sunny AI": {"price": 150.0, "proxy": "Google"},
    "GCBROS": {"price": 50.0, "proxy": "Microsoft"}
}

# --- 2. THE 100-EVENT GC NEWS POOL ---
NEWS_POOL = [
    {"text": "📦 Shaurya Inc. digitizes 4 petabytes of vintage 2021 chat logs into 'The Vault'.", "impact": {"Shaurya Inc": 0.03}},
    {"text": "💎 Shaurya Inc. facilitates the trade of a 1-of-1 'Golden Screenshot' for $1.2M.", "impact": {"Shaurya Inc": 0.025}},
    {"text": "🛡️ Shaurya Inc. successfully blocks a GCBROS 'Leak' attempt; market confidence up.", "impact": {"Shaurya Inc": 0.02}},
    {"text": "🎥 Sunny AI's new generator creates a 'Deepfake Shaurya' so real it confused the board.", "impact": {"Sunny AI": 0.04, "Shaurya Inc": -0.01}},
    {"text": "🎨 Sunny AI releases 'Candid GCBROS' photo pack; parody images go viral.", "impact": {"Sunny AI": 0.035, "GCBROS": -0.02}},
    {"text": "🚨 GCBROS CEO doubles down on controversial statements; volatility spikes.", "impact": {"GCBROS": 0.05}},
    {"text": "📸 GCBROS drops a 'Nuke': A high-definition screenshot from the 2022 era.", "impact": {"GCBROS": 0.04}},
    {"text": "🤝 SHAURYA-SUNNY ALLIANCE: The giants join forces to erase GCBROS' history.", "impact": {"Shaurya Inc": 0.04, "Sunny AI": 0.04, "GCBROS": -0.07}},
    {"text": "⚔️ CORPORAL WAR: Shaurya Inc. sues Sunny AI for 'Unlicensed Meme Reproduction'.", "impact": {"Shaurya Inc": -0.02, "Sunny AI": -0.02}},
    {"text": "☢️ TRI-WAR: GCBROS releases AI screenshots of Shaurya and Sunny arguing.", "impact": {"GCBROS": 0.03, "Shaurya Inc": -0.02, "Sunny AI": -0.02}},
    {"text": "💩 GCBROS accidentally leaks his own search history in a screenshot.", "impact": {"GCBROS": -0.08}},
    {"text": "💬 GCBROS sends 400 messages in 2 minutes; chat platform crashes.", "impact": {"GCBROS": 0.03}}
] + [
    {"text": f"📡 GC Insider: {random.choice(['Shaurya Inc', 'Sunny AI', 'GCBROS'])} {random.choice(['is winning the roast battle', 'posted a cringe sticker', 'is leaking receipts'])}.", 
     "impact": {random.choice(["Shaurya Inc", "Sunny AI", "GCBROS"]): random.uniform(-0.02, 0.02)}} for i in range(88)
]

# --- 3. SHARED DATA ENGINE ---
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
            # Volatility is higher during Emergency
            vol = 0.003 if is_emergency else 0.0015
            move = np.random.normal(0.0001 + boost, vol)
            market["prices"][name] *= (1 + move)
            
        market["history"].append(market["prices"].copy())
        if len(market["history"]) > 50: market["history"].pop(0)
        
        if random.random() < 0.30:
            if is_emergency:
                market["news"] = {"text": "🚨 EMERGENCY: HARDIYA PROTOCOL ACTIVE. MARKET IN FREEFALL.", "impact": {}}
            else:
                market["news"] = random.choice(NEWS_POOL)
        else:
            market["news"]["impact"] = {k: v*0.7 for k, v in market["news"].get("impact", {}).items()}
            
        market["last_update"] = now
        save_json(MARKET_FILE, market)
    
    return market, is_emergency

# --- 4. UI SETUP ---
st.set_page_config(page_title="Shaurya Terminal", layout="wide")
market_state, is_emergency = get_synced_market()
prices = market_state["prices"]

if is_emergency:
    st.markdown("<style>.stApp { background-color: #2b0505; }</style>", unsafe_allow_html=True)

st.markdown("""<style>
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #2d2f39; }
    .stInfo { background-color: #002b36; border-left: 5px solid #268bd2; font-family: monospace; }
</style>""", unsafe_allow_html=True)

# --- 5. MAIN TERMINAL ---
st.markdown(f"### 🏛️ SHAURYA INC. GLOBAL TERMINAL {'🔴 EMERGENCY ACTIVE' if is_emergency else '🟢 SYSTEM ONLINE'}")
st.info(f"🛰️ **WIRE:** {market_state['news']['text']}")

m_cols = st.columns(3)
for i, name in enumerate(prices):
    with m_cols[i]:
        delta_pct = 0
        if len(market_state["history"]) > 1:
            prev = market_state["history"][-2][name]
            delta_pct = ((prices[name] - prev) / prev) * 100
        
        st.metric(label=name, value=f"${prices[name]:,.2f}", delta=f"{delta_pct:.3f}%")
        original_p = STARTING_CONFIG[name]["price"]
        cap = (prices[name] / original_p) * 1000000.0
        st.write(f"Valuation: **${cap:,.2f}**")

st.line_chart(pd.DataFrame(market_state["history"]), height=300)

# --- 6. SIDEBAR: ACCOUNT & GOD MODE ---
st.sidebar.title("💳 TRADER AUTH")
users = load_json(USER_FILE, {})

if 'user' not in st.session_state:
    user_id = st.sidebar.text_input("Trader ID", placeholder="Username...")
    if st.sidebar.button("Establish Connection"):
        if user_id:
            if user_id not in users:
                users[user_id] = {"balance": 100000.0, "portfolio": {n: 0 for n in STARTING_CONFIG}}
                save_json(USER_FILE, users)
            st.session_state.user = user_id
            st.rerun()
else:
    u = users[st.session_state.user]
    net_worth = u["balance"] + sum(u["portfolio"][n] * prices[n] for n in STARTING_CONFIG)
    
    st.sidebar.success(f"ONLINE: {st.session_state.user}")
    st.sidebar.metric("Net Worth", f"${net_worth:,.2f}", delta=f"{(net_worth - 100000):,.2f}")
    st.sidebar.write(f"Cash: `${u['balance']:,.2f}`")

    # --- GOD MODE: MR. SHAURYA HARDIYA ---
    if st.session_state.user == "Mr. Shaurya Hardiya":
        st.sidebar.divider()
        st.sidebar.subheader("👑 ADMIN PANEL")
        
        last_used_ts = market_state.get("emergency_last_used", 0)
        last_date = datetime.fromtimestamp(last_used_ts)
        now_date = datetime.now()
        
        can_use = (now_date.month != last_date.month) or (now_date.year != last_date.year)
        
        if is_emergency:
            end_time = datetime.fromtimestamp(market_state["emergency_active_until"]).strftime('%H:%M:%S')
            st.sidebar.warning(f"EMERGENCY ACTIVE UNTIL {end_time}")
        elif can_use:
            if st.sidebar.button("🚨 TRIGGER EMERGENCY", use_container_width=True):
                # Apply the massive drop
                for name in market_state["prices"]:
                    drop = 0.80 if name == "Shaurya Inc" else 0.60
                    market_state["prices"][name] *= drop
                
                market_state["emergency_active_until"] = time.time() + (4 * 86400)
                market_state["emergency_last_used"] = time.time()
                save_json(MARKET_FILE, market_state)
                st.rerun()
        else:
            st.sidebar.info("EMERGENCY COOLDOWN: 1 USE PER MONTH")

    # --- TRADING UI ---
    st.sidebar.divider()
    tgt = st.sidebar.selectbox("Execute Order", list(STARTING_CONFIG.keys()))
    amt = st.sidebar.number_input("Quantity", min_value=0, step=1)
    
    b, s = st.sidebar.columns(2)
    if b.button("BUY", use_container_width=True):
        cost = amt * prices[tgt]
        if u["balance"] >= cost and amt > 0:
            u["balance"] -= cost
            u["portfolio"][tgt] += amt
            save_json(USER_FILE, users)
            st.rerun()
    if s.button("SELL", use_container_width=True):
        if u["portfolio"].get(tgt, 0) >= amt and amt > 0:
            u["balance"] += (amt * prices[tgt])
            u["portfolio"][tgt] -= amt
            save_json(USER_FILE, users)
            st.rerun()

# --- 7. AUTO-REFRESH ---
time.sleep(10)
st.rerun()