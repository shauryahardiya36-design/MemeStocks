import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import time
import random

# --- 1. FIXED MARKET CONSTANTS ---
# Initial Setup: Price | Proxy | Ticker
STARTING_CONFIG = {
    "Shaurya Inc": {"price": 100.0, "proxy": "Nvidia", "base_cap": 1000000.0},
    "Sunny AI": {"price": 150.0, "proxy": "Google", "base_cap": 1000000.0},
    "GCBROS": {"price": 50.0, "proxy": "Microsoft", "base_cap": 1000000.0}
}

NEWS_POOL = [
    "📰 Shaurya Inc (NVDA) inventory surge: 50,000 rare screenshots moved to cold storage.",
    "🗣️ GCBROS (MSFT) CEO issues controversial 'Simulation Theory' statement on livestream.",
    "🎨 Sunny AI (GOOGL) leaks 'Candid GCBROS' photo pack; parity AI images go viral.",
    "🚀 Shaurya Inc. hits new peak as 'Golden Wojak' trade clears for record numbers.",
    "⚠️ GCBROS platform restricted following late-night 'unfiltered' rant by founders.",
    "🎥 Sunny AI's new generator creates a 'Deepfake Shaurya' so real it confused the board."
]

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f: return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f: json.dump(users, f, indent=4)

# --- 2. INITIALIZATION ---
st.set_page_config(page_title="Shaurya Live Terminal", layout="wide")

if 'market_data' not in st.session_state:
    # Set the initial state exactly as requested
    st.session_state.market_data = {
        name: {
            "price": info["price"],
            "cap": info["base_cap"],
            "proxy": info["proxy"],
            "start_price": info["price"]
        } for name, info in STARTING_CONFIG.items()
    }
    st.session_state.history = pd.DataFrame([{t: STARTING_CONFIG[t]["price"] for t in STARTING_CONFIG}])
    st.session_state.current_news = "Market is Live. All companies initialized at $1.00M Cap."

# --- 3. THE LIVE LOOP ---
placeholder = st.empty()

while True:
    with placeholder.container():
        st.title("🏛️ Shaurya Inc. Real-Time Terminal")
        
        # Rotational News Bar (Professional Blue Ribbon)
        st.info(f"**LIVE WIRE:** {st.session_state.current_news}")
        
        # 4. MARKET METRICS (Updates every 30s)
        cols = st.columns(3)
        for i, (name, data) in enumerate(st.session_state.market_data.items()):
            # Calculate movement (Random Walk with tiny drift)
            move = np.random.normal(0.0002, 0.001) 
            data["price"] *= (1 + move)
            
            # MATH: Cap increases/decreases proportionally to the price change
            # (New Price / Original Price) * $1M Starting Cap
            original_price = STARTING_CONFIG[name]["price"]
            data["cap"] = (data["price"] / original_price) * 1000000.0
            
            with cols[i]:
                st.metric(label=f"{name} ({data['proxy']})", 
                          value=f"${data['price']:.2f}", 
                          delta=f"{move*100:.3f}%")
                st.write(f"Market Cap: **${data['cap']:,.2f}**")

        # 5. LIVE CHART
        new_row = {t: st.session_state.market_data[t]["price"] for t in STARTING_CONFIG}
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True).iloc[-50:]
        st.line_chart(st.session_state.history)

        # 6. SIDEBAR & USER DATA
        st.sidebar.title("💳 Trader Access")
        users = load_users()
        if 'user' not in st.session_state:
            user_id = st.sidebar.text_input("Enter ID")
            if st.sidebar.button("Login"):
                if user_id:
                    if user_id not in users:
                        users[user_id] = {"balance": 100000.0, "portfolio": {t: 0 for t in STARTING_CONFIG}}
                        save_users(users)
                    st.session_state.user = user_id
                    st.rerun()
        else:
            u = users[st.session_state.user]
            st.sidebar.success(f"User: {st.session_state.user}")
            st.sidebar.metric("Balance", f"${u['balance']:,.2f}")
            
            # Simple Trade Logic in Sidebar
            with st.sidebar.expander("Execute Trade"):
                tgt = st.selectbox("Ticker", list(STARTING_CONFIG.keys()))
                amt = st.number_input("Shares", min_value=0, step=1)
                cp = st.session_state.market_data[tgt]["price"]
                if st.button("Buy"):
                    if u["balance"] >= (amt * cp):
                        u["balance"] -= (amt * cp); u["portfolio"][tgt] += amt
                        save_users(users); st.rerun()
                if st.button("Sell"):
                    if u["portfolio"][tgt] >= amt:
                        u["balance"] += (amt * cp); u["portfolio"][tgt] -= amt
                        save_users(users); st.rerun()

        # Update News every loop (100% chance to cycle news every 30s)
        st.session_state.current_news = random.choice(NEWS_POOL)
        
        # WAIT 30 SECONDS
        time.sleep(30)
        st.rerun()