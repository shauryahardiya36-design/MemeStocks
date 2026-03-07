import streamlit as st
import json
import os
import random
import pandas as pd

# --- CONFIGURATION ---
INITIAL_BALANCE = 100000.0
USERS_FILE = "users.json"

# Lore Company -> Real World Proxy
MAPPING = {
    "Shaurya Inc": {"proxy": "NVIDIA ($NVDA)", "base_price": 100.0},
    "Sunny AI": {"proxy": "Google ($GOOGL)", "base_price": 150.0},
    "GCBROS": {"proxy": "Microsoft ($MSFT)", "base_price": 50.0}
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
    """Simulates market movement for all companies based on their proxies."""
    if 'market_data' not in st.session_state:
        st.session_state.market_data = {
            name: {"price": info["base_price"], "cap": 1000000.0, "proxy": info["proxy"]}
            for name, info in MAPPING.items()
        }
        # Initialize history for charts
        st.session_state.history = pd.DataFrame(columns=list(MAPPING.keys()))

    # Move the market for EVERY company
    new_row = {}
    for name in st.session_state.market_data:
        # Simulate the proxy move (-2.5% to +2.5%)
        move = random.uniform(-0.025, 0.025)
        
        st.session_state.market_data[name]["price"] *= (1 + move)
        st.session_state.market_data[name]["cap"] *= (1 + move)
        st.session_state.market_data[name]["last_move"] = move * 100
        new_row[name] = st.session_state.market_data[name]["price"]

    # Update history log
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
    return st.session_state.market_data

def main():
    st.set_page_config(page_title="Shaurya Inc. Terminal", page_icon="🏛️", layout="wide")
    st.title("🏛️ Shaurya Inc. Real-Time Exchange")
    
    # Update market on every interaction to keep it dynamic
    market = update_market()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.header("Terminal Login")
        username = st.text_input("Enter Username")
        if st.button("Login"):
            users = load_users()
            
            # Global Reset Logic
            st.session_state.balance = INITIAL_BALANCE
            if username in users:
                st.session_state.portfolio = users[username]['portfolio']
            else:
                st.session_state.portfolio = {c: 0 for c in MAPPING.keys()}
            
            users[username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}
            save_users(users)
            
            st.session_state.username = username
            st.session_state.logged_in = True
            st.rerun()
    else:
        # Sidebar
        st.sidebar.header(f"👤 {st.session_state.username}")
        st.sidebar.metric("Cash Balance", f"${st.session_state.balance:,.2f}")
        
        action = st.sidebar.radio("Navigation", ["Market Watch", "Trade", "Portfolio", "Logout"])

        if action == "Market Watch":
            st.header("📈 Live Market Performance")
            
            # Performance Cards
            cols = st.columns(3)
            for i, (name, data) in enumerate(market.items()):
                with cols[i]:
                    st.metric(label=f"{name} ({data['proxy']})", 
                              value=f"${data['price']:.2f}", 
                              delta=f"{data['last_move']:.2f}%")
                    st.caption(f"Valuation: ${data['cap']:,.2f}")
            
            st.divider()
            
            # Real-Time Chart
            st.subheader("Market Trends")
            st.line_chart(st.session_state.history)
            
            if st.button("Manual Refresh (Market Tick)"):
                st.rerun()

        elif action == "Trade":
            st.header("⚡ Execute Trade")
            company = st.selectbox("Select Asset", list(market.keys()))
            price = market[company]['price']
            owned = st.session_state.portfolio.get(company, 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{company}** Price: `${price:.2f}`")
                amt_buy = st.number_input("Shares to Buy", min_value=0, step=1)
                if st.button("Confirm Buy"):
                    cost = amt_buy * price
                    if cost > st.session_state.balance:
                        st.error("Insufficient Cash.")
                    elif amt_buy > 0:
                        st.session_state.balance -= cost
                        st.session_state.portfolio[company] += amt_buy
                        users = load_users(); users[st.session_state.username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}; save_users(users)
                        st.success("Buy Order Filled.")
                        st.rerun()

            with col2:
                st.write(f"Owned: `{owned}` shares")
                amt_sell = st.number_input("Shares to Sell", min_value=0, max_value=max(0, owned), step=1)
                if st.button("Confirm Sell"):
                    if owned >= amt_sell and amt_sell > 0:
                        st.session_state.balance += (amt_sell * price)
                        st.session_state.portfolio[company] -= amt_sell
                        users = load_users(); users[st.session_state.username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}; save_users(users)
                        st.success("Sell Order Filled.")
                        st.rerun()

        elif action == "Portfolio":
            st.header("📊 Your Wealth")
            total_holdings = 0
            for name, shares in st.session_state.portfolio.items():
                if shares > 0:
                    val = shares * market[name]['price']
                    total_holdings += val
                    st.write(f"**{name}**: {shares} shares — `${val:,.2f}`")
            
            st.divider()
            st.metric("Total Net Worth", f"${st.session_state.balance + total_holdings:,.2f}")

        elif action == "Logout":
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()