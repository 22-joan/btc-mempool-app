import streamlit as st
import requests
import pandas as pd
import time

# ⚡ Configuración
BTC_THRESHOLD = 0.02  # umbral en BTC
URL = "https://blockchain.info/unconfirmed-transactions?format=json"

st.title("Transacciones BTC > 0.02 BTC")

# Función para obtener transacciones grandes
def get_large_txs():
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        large_txs = []
        for tx in data.get("txs", []):
            total_out = sum(out["value"] for out in tx.get("out", [])) / 1e8
            if total_out >= BTC_THRESHOLD:
                large_txs.append({
                    "txid": tx["hash"],
                    "total_out_btc": total_out,
                    "fee_btc": tx["fee"]/1e8,
                    "size_bytes": tx["size"],
                    "time": pd.to_datetime(tx["time"], unit='s')
                })
        return large_txs
    except Exception as e:
        st.error(f"Error al obtener transacciones: {e}")
        return []

# Botón para actualizar
if st.button("Actualizar transacciones"):
    st.info("Obteniendo datos...")
    txs = get_large_txs()
    if txs:
        df = pd.DataFrame(txs)
        st.dataframe(df)  # Muestra la tabla
    else:
        st.warning("No se encontraron transacciones que superen el umbral.")

