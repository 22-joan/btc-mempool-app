import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

BTC_THRESHOLD = 0.03  # Umbral en BTC
st.title("Transacciones de Bitcoin > 0,03 BTC en las últimas 24h")

# Botón para actualizar datos
actualizar = st.button("Actualizar ahora")

# Solo se ejecuta cuando se pulsa el botón
if actualizar:
    limite_timestamp = int((datetime.utcnow() - timedelta(days=1)).timestamp())

    try:
        # API Blockstream: últimos bloques
        blocks = requests.get("https://blockstream.info/api/blocks").json()

        tx_list = []

        for block in blocks:
            block_time = block["timestamp"]
            if block_time < limite_timestamp:
                break

            block_hash = block["id"]
            txs = requests.get(f"https://blockstream.info/api/block/{block_hash}/txs").json()

            for tx in txs:
                total_out = sum(o.get("value", 0) for o in tx.get("vout", [])) / 1e8
                if total_out >= BTC_THRESHOLD:
                    tx_list.append({
                        "txid": tx["txid"],
                        "total_out_btc": total_out,
                        "fee_btc": tx.get("fee", 0) / 1e8,
                        "size_bytes": tx.get("size", 0),
                        "time": datetime.utcfromtimestamp(block_time)
                    })

        if tx_list:
            df = pd.DataFrame(tx_list)
            st.dataframe(df)
        else:
            st.info("No hay transacciones en las últimas 24h que superen 0,03 BTC.")

    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
