import streamlit as st
import json
import os
import random

# Fixed starting points, but we'll simulate a 1% "market movement" on each refresh
BASE_PRICES = {"Shaurya Inc": 100.0, "Sunny AI": 150.0, "GCBROS": 50.0}
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_market_prices():
    """Simulates a small random fluctuation for the current session."""
    if 'current_prices' not in st.session_state:
        st.session_state.current_prices = BASE_PRICES.copy()
    
    # Randomly fluctuate prices by +/- 1.5% each time the app logic runs
    for company in st.session_state.current_prices:
        change = random.uniform(-0.015, 0.015)
        st.session_state.current_prices[company] *= (1 + change)
    
    return st.session_state.current_prices

def main():
    st.set_page_config(page_title="Shaurya Inc. Exchange", page_icon="📈")
    st.title("📈 Shaurya Inc. Stock Simulator")
    
    # Initialize prices for this run
    prices = get_market_prices()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.header("Login")
        username = st.text_input("Enter your username (or create a new one)")
        if st.button("Login"):
            users = load_users()
            if username in users:
                st.session_state.balance = users[username]['balance']
                st.session_state.portfolio = users[username]['portfolio']
                st.success(f"Welcome back, {username}!")
            else:
                # Default starting balance for new traders
                st.session_state.balance = 10000.0 
                st.session_state.portfolio = {"Shaurya Inc": 0, "GCBROS": 0, "Sunny AI": 0}
                users[username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}
                save_users(users)
                st.success(f"Welcome to the market, {username}!")
            
            st.session_state.username = username
            st.session_state.logged_in = True
            st.rerun()
    else:
        # Sidebar for actions
        st.sidebar.header(f"👤 {st.session_state.username}")
        st.sidebar.write(f"Balance: **${st.session_state.balance:,.2f}**")
        
        action = st.sidebar.selectbox("Choose action", 
            ["View Prices", "Buy Stock", "Sell Stock", "View Portfolio", "Logout"])

        if action == "View Prices":
            st.header("📊 Market Overview")
            cols = st.columns(3)
            
            # Display metrics with random 'deltas' for visual effect
            for i, (company, price) in enumerate(prices.items()):
                delta = random.uniform(-2.5, 2.5)
                cols[i].metric(label=company, value=f"${price:.2f}", delta=f"{delta:.2f}%")
            
            st.info("Prices fluctuate slightly every time you interact with the app!")

        elif action == "Buy Stock":
            st.header("🛒 Buy Shares")
            company = st.selectbox("Select company", list(prices.keys()))
            current_price = prices[company]
            
            st.write(f"Current Price: **${current_price:.2f}**")
            shares = st.number_input("Number of shares", min_value=1, step=1)
            cost = shares * current_price
            
            st.write(f"Total Cost: **${cost:,.2f}**")
            if st.button("Confirm Purchase"):
                if cost > st.session_state.balance:
                    st.error(f"Insufficient funds! You need ${cost:,.2f}")
                else:
                    st.session_state.balance -= cost
                    st.session_state.portfolio[company] += shares
                    
                    # Update JSON file
                    users = load_users()
                    users[st.session_state.username]['balance'] = st.session_state.balance
                    users[st.session_state.username]['portfolio'] = st.session_state.portfolio
                    save_users(users)
                    st.success(f"Successfully bought {shares} shares of {company}!")

        elif action == "Sell Stock":
            st.header("💸 Sell Shares")
            company = st.selectbox("Select company", list(prices.keys()))
            current_price = prices[company]
            max_shares = st.session_state.portfolio.get(company, 0)
            
            st.write(f"You own: **{max_shares}** shares")
            shares = st.number_input("Shares to sell", min_value=1, max_value=max_shares if max_shares > 0 else 1, step=1)
            revenue = shares * current_price
            
            st.write(f"Expected Revenue: **${revenue:,.2f}**")
            if st.button("Confirm Sale"):
                if max_shares <= 0:
                    st.error("You don't own any shares of this company!")
                else:
                    st.session_state.balance += revenue
                    st.session_state.portfolio[company] -= shares
                    
                    # Update JSON file
                    users = load_users()
                    users[st.session_state.username]['balance'] = st.session_state.balance
                    users[st.session_state.username]['portfolio'] = st.session_state.portfolio
                    save_users(users)
                    st.success(f"Successfully sold {shares} shares of {company}!")

        elif action == "View Portfolio":
            st.header("💼 Your Portfolio")
            st.write(f"**Cash Balance**: ${st.session_state.balance:,.2f}")
            
            total_holdings_value = 0
            portfolio_data = []
            
            for company, shares in st.session_state.portfolio.items():
                value = shares * prices[company]
                total_holdings_value += value
                if shares > 0:
                    portfolio_data.append({"Company": company, "Shares": shares, "Current Value": f"${value:,.2f}"})
            
            if portfolio_data:
                st.table(portfolio_data)
            else:
                st.write("Your portfolio is currently empty.")
                
            st.subheader(f"Total Portfolio Value: ${st.session_state.balance + total_holdings_value:,.2f}")

        elif action == "Logout":
            st.session_state.logged_in = False
            st.info("Progress saved. See you next time!")
            st.rerun()

if __name__ == "__main__":
    main()