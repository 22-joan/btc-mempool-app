import streamlit as st
import pandas as pd
import requests
import time

# ---------------------------
# Configuración de la app
# ---------------------------
st.set_page_config(page_title="Bitcoin Mempool Monitor", layout="wide")
st.title("🔶 Transacciones BTC > 0.02 BTC")

# Umbral mínimo en BTC
BTC_THRESHOLD = 0.02

# Endpoint de mempool (blockchain.info)
URL = "https://blockchain.info/unconfirmed-transactions?format=json"

# Función para obtener transacciones grandes
def get_large_txs():
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        large_txs = []
        for tx in data.get("txs", []):
            total_out = sum(out["value"] for out in tx.get("out", []))
            total_btc = total_out / 1e8
            if total_btc >= BTC_THRESHOLD:
                large_txs.append({
                    "txid": tx["hash"],
                    "total_btc": total_btc,
                    "fee_btc": tx["fee"] / 1e8,
                    "size_bytes": tx["size"],
                    "time": pd.to_datetime(tx["time"], unit='s')
                })
        return large_txs
    except Exception as e:
        st.error(f"Error al obtener transacciones: {e}")
        return []

# ---------------------------
# Sesión para guardar transacciones
# ---------------------------
if "txs" not in st.session_state:
    st.session_state.txs = []

# Botón manual para actualizar
if st.button("🔄 Actualizar transacciones"):
    st.session_state.txs = get_large_txs()

# Auto-refresh cada 10 segundos
placeholder = st.empty()
for _ in range(1):  # Solo 1 loop para Streamlit, se puede activar con cron externo
    txs = get_large_txs()
    if txs:
        st.session_state.txs = txs
    # Mostrar tabla
    df = pd.DataFrame(st.session_state.txs)
    placeholder.dataframe(df, use_container_width=True)
    time.sleep(10)  # Espera 10 segundos antes de siguiente actualización
