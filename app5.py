import streamlit as st
from web3 import Web3
import json

# --- 1. SETTINGS & SECRETS ---
# Ensure these match exactly what you put in your Streamlit Cloud Secrets
try:
    RPC_URL = st.secrets["RPC_URL"]
    PRIVATE_KEY = st.secrets["PRIVATE_KEY"]
    CONTRACT_ADDRESS = st.secrets["CONTRACT_ADDRESS"]
except Exception as e:
    st.error("Secrets not found! Make sure RPC_URL, PRIVATE_KEY, and CONTRACT_ADDRESS are set.")
    st.stop()

# --- 2. BLOCKCHAIN CONNECTION ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load ABI (Ensure abi.json is in your src/ folder)
with open("src/abi.json", "r") as f:
    contract_abi = json.load(f)

# Initialize Contract Instance
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Futures v5 - Live", layout="wide")
st.title("⚡ Futures Smart Contract Terminal")

st.sidebar.header("Wallet Info")
st.sidebar.info(f"Connected Address: \n{account.address}")
balance = w3.eth.get_balance(account.address)
st.sidebar.metric("Balance", f"{w3.from_wei(balance, 'ether'):.4f} ETH")

# --- 4. TRADING INTERFACE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Open Position")
    amount = st.number_input("Amount (ETH)", min_value=0.01, value=0.1, step=0.01)
    leverage = st.slider("Leverage", 1, 20, 5)
    
    # Example logic: calling a function from your Solidity contract
    if st.button("Confirm Trade"):
        with st.spinner("Signing and sending transaction..."):
            try:
                # Build the transaction
                nonce = w3.eth.get_transaction_count(account.address)
                # Replace 'openPosition' with the exact function name in your Solidity file
                txn = contract.functions.openPosition().build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gas': 300000,
                    'gasPrice': w3.eth.gas_price
                })
                
                # Sign and Send
                signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                st.success(f"Trade Success! Hash: {tx_hash.hex()}")
                st.balloons()
            except Exception as e:
                st.error(f"Transaction failed: {str(e)}")

with col2:
    st.subheader("Live Market Data")
    # In a real app, you would fetch this from an API like Binance or CoinGecko
    st.metric(label="Current ETH Price", value="$2,485.20", delta="1.4%")
    st.line_chart([2410, 2435, 2420, 2460, 2485])
