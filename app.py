import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="BTC Mempool >1 BTC", layout="wide")
st.title("Transacciones BTC en Mempool > 1 BTC")

BTC_THRESHOLD = 1  # 1 BTC
API_URL = "https://mempool.space/api/mempool/recent"

# Tabla de transacciones
if "txs" not in st.session_state:
    st.session_state.txs = []

def fetch_large_txs():
    try:
        resp = requests.get(API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        large_txs = []
        for tx in data:
            total_btc = sum(vout["value"] for vout in tx["vout"]) / 1e8
            if total_btc >= BTC_THRESHOLD:
                large_txs.append({
                    "txid": tx["txid"],
                    "total_btc": total_btc,
                    "size": tx["size"]
                })
        return large_txs
    except Exception as e:
        st.error(f"Error al consultar mempool: {e}")
        return []

# Botón para actualizar
if st.button("Actualizar transacciones"):
    st.session_state.txs = fetch_large_txs()

# Mostrar tabla
df = pd.DataFrame(st.session_state.txs)
st.dataframe(df)

