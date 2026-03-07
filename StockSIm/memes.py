import streamlit as st
import json
import os
import pandas as pd
import random

# --- 1. THE NEWS ENGINE (5 per company) ---
NEWS_DATABASE = {
    "Shaurya Inc": [
        {"t": "💎 Shaurya Inc. facilitates the trade of a 1-of-1 'Golden Screenshot' for $1.2M.", "impact": 0.08},
        {"t": "📦 Meme Inventory Update: Shaurya Inc. digitizes 4 petabytes of vintage group chat logs.", "impact": 0.03},
        {"t": "🚨 Market Alert: Shaurya Inc. declares a 'Screenshot Dividend' for long-term holders.", "impact": 0.05},
        {"t": "📉 Shaurya Inc. valuation dips as rival 'Save-As' cartel attempts a screenshot heist.", "impact": -0.04},
        {"t": "🏛️ Shaurya Inc. expands into 'Legacy Memes'—exclusive rights to 2012-era archives secured.", "impact": 0.06}
    ],
    "Sunny AI": [
        {"t": "🎨 Sunny AI's 'Real-Life Shaurya' photo series goes viral; AI-generated parodies flood the market.", "impact": 0.05},
        {"t": "🎥 BREAKING: Sunny AI releases high-fidelity video of GCBROS arguing with a toaster.", "impact": 0.04},
        {"t": "🤖 Sunny AI's new 'Meme-Generator' plugin leads to a 400% increase in content output.", "impact": 0.07},
        {"t": "⚠️ Sunny AI servers overheat during a 24-hour render of Shaurya Inc's logo; downtime reported.", "impact": -0.03},
        {"t": "📸 Sunny AI creates 'The Ultimate GCBROS Parody'—the AI video is so realistic it's legally confusing.", "impact": 0.05}
    ],
    "GCBROS": [
        {"t": "🚨 GCBROS CEO issues 'Final Warning' after late-night racial tirade; stock enters freefall.", "impact": -0.12},
        {"t": "🗣️ GCBROS claims 'the moon is a Sunny AI projection'—controversy drives massive engagement.", "impact": -0.04},
        {"t": "📈 Investors ignore GCBROS controversy to bet on upcoming 'Funny AI Video' leaked roadmap.", "impact": 0.03},
        {"t": "🚫 GCBROS banned from 4 major platforms; 'Shadow Trading' volume reaches all-time high.", "impact": -0.10},
        {"t": "📺 GCBROS 'Unfiltered' livestream breaks the internet; controversial statements spark $20M in trades.", "impact": 0.02}
    ]
}

# --- 2. CORE FUNCTIONS ---
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f: return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f: json.dump(users, f, indent=4)

def trigger_news():
    """Picks a random company, triggers a news event, and shifts its price."""
    company = random.choice(list(NEWS_DATABASE.keys()))
    event = random.choice(NEWS_DATABASE[company])
    
    st.session_state.current_news = event['t']
    st.session_state.market_data[company]["price"] *= (1 + event["impact"])
    
    # Update chart history
    new_row = {t: st.session_state.market_data[t]["price"] for t in st.session_state.market_data}
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True).iloc[-50:]

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Shaurya Global Terminal", layout="wide")
st.title("🏛️ Shaurya Inc. Global Terminal")

# Initialization
if 'market_data' not in st.session_state:
    st.session_state.market_data = {
        "Shaurya Inc": {"price": 10.50},
        "Sunny AI": {"price": 25.00},
        "GCBROS": {"price": 15.75}
    }
    st.session_state.history = pd.DataFrame([{t: 10.0 for t in NEWS_DATABASE.keys()}])
    st.session_state.current_news = "Market is Open. Trading memes and AI content at scale."

# Display News Bar
st.info(f"**LATEST WIRE:** {st.session_state.current_news}")

# User Logic
users = load_users()
if 'user' not in st.session_state:
    user = st.sidebar.text_input("Enter Trader ID")
    if st.sidebar.button("Login"):
        if user not in users:
            users[user] = {"balance": 100000.0, "portfolio": {t: 0 for t in NEWS_DATABASE.keys()}}
            save_users(users)
        st.session_state.user = user
        st.rerun()
else:
    u_data = users[st.session_state.user]
    st.sidebar.metric("Buying Power", f"${u_data['balance']:,.2f}")
    
    # Market Metrics
    cols = st.columns(3)
    for i, t in enumerate(NEWS_DATABASE.keys()):
        price = st.session_state.market_data[t]["price"]
        cols[i].metric(t, f"${price:,.2f}")

    st.line_chart(st.session_state.history)

    # Trading Area
    with st.expander("⚡ Market Operations"):
        target = st.selectbox("Asset", list(NEWS_DATABASE.keys()))
        amt = st.number_input("Shares", min_value=0, step=1)
        curr_p = st.session_state.market_data[target]["price"]
        
        b, s = st.columns(2)
        if b.button("EXECUTE BUY"):
            if u_data["balance"] >= (amt * curr_p):
                u_data["balance"] -= (amt * curr_p)
                u_data["portfolio"][target] += amt
                save_users(users); st.rerun()
        if s.button("LIQUIDATE"):
            if u_data["portfolio"][target] >= amt:
                u_data["balance"] += (amt * curr_p)
                u_data["portfolio"][target] -= amt
                save_users(users); st.rerun()

    # Manual Refresh moves the market
    if st.button("🔄 Refresh Terminal (New News Drop)"):
        trigger_news()
        st.rerun()