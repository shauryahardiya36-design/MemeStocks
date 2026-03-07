import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random

# --- 1. MARKET ARCHITECTURE ---
# Shaurya Inc = Nvidia | Sunny AI = Google | GCBROS = Microsoft
STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "proxy": "Nvidia", "base_cap": 1000000.0},
    "Sunny AI": {"price": 150.0, "proxy": "Google", "base_cap": 1000000.0},
    "GCBROS": {"price": 50.0, "proxy": "Microsoft", "base_cap": 1000000.0}
}

NEWS_POOL = [
    "💎 Shaurya Inc. facilitates the trade of a 1-of-1 'Golden Screenshot' for $1.2M.",
    "🚨 GCBROS CEO doubles down on controversial statements; market volatility spikes.",
    "🎨 Sunny AI releases 'Candid GCBROS' photo pack; parody images go viral globally.",
    "📦 Shaurya Inc. digitizes 4 petabytes of vintage group chat logs into the 'Vault'.",
    "🎥 Sunny AI's new generator creates a 'Deepfake Shaurya' so real it confused the board.",
    "⚠️ GCBROS platform restricted in 3 countries after 'unfiltered' midnight rant.",
    "🚀 Shaurya Inc (NVDA) inventory surge: 50,000 rare screenshots moved to cold storage."
]

# --- 2. DATA UTILITIES ---
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f: return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f: json.dump(users, f, indent=4)

# --- 3. UI INITIALIZATION ---
st.set_page_config(page_title="Shaurya Terminal", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a professional "Dark Bloom" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #2d2f39; }
    .stInfo { background-color: #002b36; border-left: 5px solid #268bd2; }
    </style>
    """, unsafe_allow_html=True)

if 'market_data' not in st.session_state:
    st.session_state.market_data = {
        name: {
            "price": info["price"],
            "cap": info["base_cap"],
            "proxy": info["proxy"]
        } for name, info in STARTING_CONFIG.items()
    }
    st.session_state.history = pd.DataFrame([{t: STARTING_CONFIG[t]["price"] for t in STARTING_CONFIG}])
    st.session_state.current_news = "SYSTEM ONLINE: Market initialized at $1.00M Cap per sector."

# --- 4. THE LIVE ENGINE ---
# This placeholder allows us to refresh the UI without a full page reload
placeholder = st.empty()

while True:
    with placeholder.container():
        st.markdown("### 🏛️ SHAURYA INC. GLOBAL REAL-TIME TERMINAL")
        
        # Professional News Ribbon
        st.info(f"🛰️ **WIRE:** {st.session_state.current_news}")
        
        # 5. LIVE MARKET METRICS
        m_cols = st.columns(3)
        for i, (name, data) in enumerate(st.session_state.market_data.items()):
            # Calculate smooth drift (0.1% to 0.5% max)
            move = np.random.normal(0.0001, 0.0008)
            data["price"] *= (1 + move)
            
            # MATH: Cap scales with price relative to the $1M start
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
        st.line_chart(st.session_state.history, height=250)

        # 7. SIDEBAR: ACCOUNT & SECURE TRADING
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
            st.sidebar.success(f"ONLINE: {st.session_state.user}")
            st.sidebar.metric("Available Cash", f"${u['balance']:,.2f}")
            
            st.sidebar.divider()
            st.sidebar.subheader("⚡ Execute Order")
            
            tgt = st.sidebar.selectbox("Select Asset", list(STARTING_CONFIG.keys()))
            curr_price = st.session_state.market_data[tgt]["price"]
            owned = u["portfolio"].get(tgt, 0)
            
            st.sidebar.write(f"Currently Held: `{owned}` shares")
            
            # Transaction Inputs
            amt = st.sidebar.number_input("Quantity", min_value=0, step=1)
            
            btn_buy, btn_sell = st.sidebar.columns(2)
            
            if btn_buy.button("BUY", use_container_width=True):
                cost = amt * curr_price
                if u["balance"] >= cost and amt > 0:
                    u["balance"] -= cost
                    u["portfolio"][tgt] += amt
                    save_users(users)
                    st.toast(f"Purchased {amt} shares of {tgt}")
                else:
                    st.sidebar.error("Insufficient Funds")

            # FIXED EXPLOIT: Check if shares owned >= shares being sold
            if btn_sell.button("SELL", use_container_width=True):
                if owned >= amt and amt > 0:
                    u["balance"] += (amt * curr_price)
                    u["portfolio"][tgt] -= amt
                    save_users(users)
                    st.toast(f"Liquidated {amt} shares of {tgt}")
                else:
                    st.sidebar.error(f"❌ Exploit Blocked: You only have {owned} shares.")

        # 8. BACKGROUND UPDATES
        if random.random() < 0.15: # 15% chance to rotate news every tick
            st.session_state.current_news = random.choice(NEWS_POOL)
        
        # SLEEP FOR 30 SECONDS
        time.sleep(30)
        st.rerun()