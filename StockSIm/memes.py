import streamlit as st
import json
import os

# Fixed stock prices
PRICES = {"Shaurya Inc": 100, "Sunny AI": 150, "GCBROS": 50}
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def main():
    st.title("📈 Stock Simulator")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.header("Login")
        username = st.text_input("Enter your username")
        if st.button("Login"):
            users = load_users()
            if username in users:
                st.session_state.balance = users[username]['balance']
                st.session_state.portfolio = users[username]['portfolio']
                st.success(f"Welcome back, {username}!")
            else:
                st.session_state.balance = 100000
                st.session_state.portfolio = {"Shaurya Inc": 0, "GCBROS": 0, "Sunny AI": 0}
                users[username] = {'balance': st.session_state.balance, 'portfolio': st.session_state.portfolio}
                save_users(users)
                st.success(f"Welcome, new user {username}!")
            st.session_state.username = username
            st.session_state.logged_in = True
            st.rerun()
    else:
        # Sidebar for actions
        st.sidebar.header("Actions")
        action = st.sidebar.selectbox("Choose action", ["View Prices", "Buy Stock", "Sell Stock", "View Portfolio", "Logout"])

        if action == "View Prices":
            st.header("📈 Current Stock Prices")
            for company, price in PRICES.items():
                st.write(f"**{company}**: ${price:.2f}")

        elif action == "Buy Stock":
            st.header("🛒 Buy Stock")
            company = st.selectbox("Select company", list(PRICES.keys()))
            shares = st.number_input("Number of shares", min_value=1, step=1)
            cost = shares * PRICES[company]
            st.write(f"Cost: ${cost:.2f}")
            if st.button("Buy"):
                if cost > st.session_state.balance:
                    st.error(f"Insufficient funds! You need ${cost:.2f} but have ${st.session_state.balance:.2f}")
                else:
                    st.session_state.balance -= cost
                    st.session_state.portfolio[company] += shares
                    users = load_users()
                    users[st.session_state.username]['balance'] = st.session_state.balance
                    users[st.session_state.username]['portfolio'] = st.session_state.portfolio
                    save_users(users)
                    st.success(f"Bought {shares} shares of {company} for ${cost:.2f}")

        elif action == "Sell Stock":
            st.header("💸 Sell Stock")
            company = st.selectbox("Select company", list(PRICES.keys()))
            max_shares = st.session_state.portfolio[company]
            shares = st.number_input("Number of shares", min_value=1, max_value=max_shares, step=1)
            revenue = shares * PRICES[company]
            st.write(f"Revenue: ${revenue:.2f}")
            if st.button("Sell"):
                st.session_state.balance += revenue
                st.session_state.portfolio[company] -= shares
                users = load_users()
                users[st.session_state.username]['balance'] = st.session_state.balance
                users[st.session_state.username]['portfolio'] = st.session_state.portfolio
                save_users(users)
                st.success(f"Sold {shares} shares of {company} for ${revenue:.2f}")

        elif action == "View Portfolio":
            st.header("📊 Portfolio")
            st.write(f"**Cash Balance**: ${st.session_state.balance:,.2f}")
            st.write("**Holdings**:")
            total_value = st.session_state.balance
            for company, shares in st.session_state.portfolio.items():
                value = shares * PRICES[company]
                total_value += value
                st.write(f"- {company}: {shares} shares @ ${PRICES[company]:.2f} = ${value:,.2f}")
            st.write(f"**Total Portfolio Value**: ${total_value:,.2f}")

        elif action == "Logout":
            users = load_users()
            users[st.session_state.username]['balance'] = st.session_state.balance
            users[st.session_state.username]['portfolio'] = st.session_state.portfolio
            save_users(users)
            st.session_state.logged_in = False
            st.success("Logged out and data saved!")
            st.rerun()

if __name__ == "__main__":
    main()