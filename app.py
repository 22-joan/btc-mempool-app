import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="BTC Mempool >1 BTC", layout="wide")
st.title("Transacciones de Bitcoin > 1 BTC en Mempool")

# Umbral para filtrar transacciones
BTC_THRESHOLD = 1  # 1 BTC

# Función para obtener transacciones recientes
@st.cache_data(ttl=10)
def get_recent_txs():
    try:
        url = "https://mempool.space/api/mempool/recent"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        txs = resp.json()
        filtered = []
        for tx in txs:
            # mempools.space devuelve 'vsize' y 'value' en sats
            total_btc = tx.get("value", 0) / 1e8
            if total_btc >= BTC_THRESHOLD:
                filtered.append({
                    "txid": tx["txid"],
                    "total_btc": total_btc,
                    "fee_sat": tx.get("fee", 0),
                    "size_bytes": tx.get("vsize", 0),
                    "time": pd.to_datetime(tx.get("time") * 1000, unit='ms')
                })
        return filtered
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return []

# Mostrar tabla en Streamlit
st.subheader(f"Transacciones recientes con más de {BTC_THRESHOLD} BTC")
tx_data = get_recent_txs()
if tx_data:
    df = pd.DataFrame(tx_data)
    st.dataframe(df)
else:
    st.info("No hay transacciones que superen el umbral en este momento.")

# Botón para actualizar
if st.button("Actualizar ahora"):
    st.experimental_rerun()
