import streamlit as st
import json
import os
import pandas as pd
import random

# --- CONFIGURATION ---
INITIAL_BALANCE = 100000.0
USERS_FILE = "users.json"

# Real World Performance Data (Closing data as of March 6-7, 2026)
# Shaurya Inc (NVDA) | Sunny AI (GOOGL) | GCBROS (MSFT)
MARKET_MOVES = {
    "Shaurya Inc": {"proxy": "NVIDIA ($NVDA)", "change": -0.019, "base": 100.0},
    "Sunny AI": {"proxy": "Google ($GOOGL)", "change": -0.0075, "base": 150.0},
    "GCBROS": {"proxy": "Microsoft ($MSFT)", "change": 0.0040, "base": 50.0}
}

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def update_market():
    """Calculates prices based on real-world data + a tiny 24/7 flutter."""
    if 'market_data' not in st.session_state:
        st.session_state.market_data = {}
        for name, info in MARKET_MOVES.items():
            # Initial setup with real-world closing data
            st.session_state.market_data[name] = {
                "price": info["base"] * (1 + info["change"]),
                "cap": 1000000.0 * (1 + info["change"]),
                "proxy": info["proxy"],
                "move_pct": info["change"] * 100
            }
        
        # Initialize Chart History
        st.session_state.history = pd.DataFrame([{name: st.session_state.market_data[name]["price"] for name in MARKET_MOVES}])

    # --- THE 24/7 FLUTTER ---
    # Adds a tiny random move (max 0.05%) to simulate active trading during the day
    new_prices = {}
    for name in st.session_state.market_data:
        flutter = 1 + random.uniform(-0.0005, 0.0005) 
        st.session_state.market_data[name]["price"] *= flutter
        st.session_state.market_data[name]["cap"] *= flutter
        new_prices[name] = st.session_state.market_data[name]["price"]

    # Update history for the chart
    new_row = pd.DataFrame([new_prices])
    st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
    
    # Keep the chart history to the last 50 data points
    if len(st.session_state.history) > 50:
        st.session_state.history = st.session_state.history.iloc[-50:]
        
    return st.session_state.market_data

def main():
    st.set_page_config(page_title="Shaurya Inc. Terminal", page_icon="🏛️", layout="wide")
    st.title("🏛️ Shaurya Inc. Real-Time Exchange")
    
    # Prices update slightly every time the app reruns
    market = update_market()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.header("Terminal Login")
        username = st.text_input("Enter Username")
        if st.button("Login"):
            if username:
                users = load_users()
                st.session_state.balance = INITIAL_BALANCE
                
                if username in users:
                    st.session_state.portfolio = users[username]['portfolio']
                else:
                    st.session_state.portfolio = {c: 0 for c in MARKET_MOVES.keys()}
                
                users[username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}
                save_users(users)
                
                st.session_state.username = username
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("Username required.")
    else:
        # --- SIDEBAR ---
        st.sidebar.header(f"👤 {st.session_state.username}")
        st.sidebar.metric("Cash Balance", f"${st.session_state.balance:,.2f}")
        
        nav = st.sidebar.radio("Navigation", ["Market Watch", "Trade", "Portfolio", "Logout"])

        # --- MARKET WATCH ---
        if nav == "Market Watch":
            st.header("📈 Live Market Valuations")
            st.caption("Tracking real-world proxies with 24/7 simulated activity.")
            
            cols = st.columns(3)
            for i, (name, data) in enumerate(market.items()):
                with cols[i]:
                    st.metric(label=f"{name} ({data['proxy']})", 
                              value=f"${data['price']:.2f}", 
                              delta=f"{data['move_pct']:.2f}%")
                    st.write(f"Company Value: **${data['cap']:,.2f}**")
            
            st.divider()
            st.subheader("Performance History (Live Ticks)")
            st.line_chart(st.session_state.history)
            
            if st.button("Refresh Market"):
                st.rerun()

        # --- TRADE ---
        elif nav == "Trade":
            st.header("⚡ Execute Trade")
            company = st.selectbox("Select Asset", list(market.keys()))
            price = market[company]['price']
            owned = st.session_state.portfolio.get(company, 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Buy")
                st.write(f"Price: `${price:.2f}`")
                amt_buy = st.number_input("Shares", min_value=0, step=1, key="buy_in")
                if st.button("Confirm Purchase"):
                    cost = amt_buy * price
                    if cost > st.session_state.balance:
                        st.error("Insufficient Funds.")
                    elif amt_buy > 0:
                        st.session_state.balance -= cost
                        st.session_state.portfolio[company] += amt_buy
                        users = load_users()
                        users[st.session_state.username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}
                        save_users(users)
                        st.success("Trade Successful.")
                        st.rerun()

            with col2:
                st.subheader("Sell")
                st.write(f"Owned: `{owned}`")
                amt_sell = st.number_input("Shares", min_value=0, max_value=max(0, owned), step=1, key="sell_in")
                if st.button("Confirm Sale"):
                    if owned >= amt_sell and amt_sell > 0:
                        st.session_state.balance += (amt_sell * price)
                        st.session_state.portfolio[company] -= amt_sell
                        users = load_users()
                        users[st.session_state.username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}
                        save_users(users)
                        st.success("Sale Successful.")
                        st.rerun()

        # --- PORTFOLIO ---
        elif nav == "Portfolio":
            st.header("💼 Asset Allocation")
            total_holdings_val = 0
            for name, shares in st.session_state.portfolio.items():
                if shares > 0:
                    current_val = shares * market[name]['price']
                    total_holdings_val += current_val
                    st.write(f"**{name}**: {shares} shares — `${current_val:,.2f}`")
            
            st.divider()
            st.metric("Total Net Worth", f"${st.session_state.balance + total_holdings_val:,.2f}")

        elif nav == "Logout":
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()