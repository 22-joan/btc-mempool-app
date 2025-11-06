import streamlit as st
import requests
import pandas as pd

URL = "https://blockchain.info/unconfirmed-transactions?format=json"
BTC_THRESHOLD = 1  # 1 BTC

st.title("Transacciones recientes con más de 1 BTC")

try:
    resp = requests.get(URL)
    resp.raise_for_status()
    data = resp.json()

    txs = data.get("txs", [])
    df = pd.DataFrame([{
        "txid": tx["hash"],
        "total_out_btc": sum(out.get("value", 0) for out in tx.get("out", [])) / 1e8,
        "fee_btc": tx.get("fee", 0) / 1e8,
        "size_bytes": tx.get("size", 0),
        "time": pd.to_datetime(tx.get("time", 0), unit='s')
    } for tx in txs])

    # Filtrar transacciones > umbral
    df_filtered = df[df["total_out_btc"] >= BTC_THRESHOLD]

    if not df_filtered.empty:
        st.dataframe(df_filtered)
    else:
        st.info("No hay transacciones que superen el umbral en este momento.")

except Exception as e:
    st.error(f"Error al obtener datos: {e}")

# Botón para actualizar
if st.button("Actualizar"):
    st.experimental_rerun()

