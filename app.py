import streamlit as st
import pandas as pd
import asyncio
import websockets
import json
import time

st.set_page_config(page_title="BTC Mempool >1 BTC", layout="wide")
st.title("Transacciones BTC en Mempool > 1 BTC")

MEMPOOL_WS_URL = "wss://mempool.space/api/v1/ws"

BTC_THRESHOLD = 1  # 1 BTC

# Tabla de transacciones
if "txs" not in st.session_state:
    st.session_state.txs = []

# Función para recibir transacciones por websocket
async def listen_mempool():
    async with websockets.connect(MEMPOOL_WS_URL) as ws:
        await ws.send(json.dumps({"op": "unconfirmed_sub"}))
        while True:
            msg = await ws.recv()
            tx = json.loads(msg)
            total_btc = sum(out["value"] for out in tx["vout"]) / 1e8
            if total_btc >= BTC_THRESHOLD:
                st.session_state.txs.append({
                    "txid": tx["txid"],
                    "total_btc": total_btc,
                    "size": tx["size"]
                })
                # Limitar a las últimas 50 txs
                st.session_state.txs = st.session_state.txs[-50:]
                st.experimental_rerun()

# Mostrar tabla
df = pd.DataFrame(st.session_state.txs)
st.dataframe(df)

# Botón para iniciar websocket
if st.button("Conectar al Mempool"):
    asyncio.run(listen_mempool())
