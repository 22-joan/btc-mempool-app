import streamlit as st
import pandas as pd
import asyncio
import websockets
import json
import time

st.set_page_config(page_title="BTC Mempool Live >1 BTC", layout="wide")
st.title("Transacciones de Bitcoin > 1 BTC en Mempool")

# ----------------------------
# Configuración
# ----------------------------
BTC_THRESHOLD = 100_000_000  # 1 BTC en satoshis

SEND_TO_AIRTABLE = False  # Cambiar a True si quieres enviar a Airtable
AIRTABLE_BASE_ID = "TU_BASE_ID"  # Opcional
AIRTABLE_API_KEY = "TU_API_KEY"
TABLE_NAME = "Transactions"
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}", "Content-Type": "application/json"}

# ----------------------------
# Función Airtable
# ----------------------------
import requests

def send_to_airtable(tx):
    record = {
        "fields": {
            "TXID": tx["TXID"],
            "Total BTC": tx["Total BTC"],
            "Fee BTC": tx["Fee BTC"],
            "Size": tx["Size"],
            "Time": tx["Time"]
        }
    }
    response = requests.post(AIRTABLE_URL, headers=HEADERS, json=record)
    if response.status_code not in (200, 201):
        print("Error Airtable:", response.status_code, response.text)

# ----------------------------
# Tabla en memoria
# ----------------------------
tx_table = pd.DataFrame(columns=["TXID", "Total BTC", "Fee BTC", "Size", "Time"])
placeholder = st.empty()

# ----------------------------
# Función principal
# ----------------------------
async def monitor_mempool():
    global tx_table
    url = "wss://mempool.space/api/v1/ws"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"op": "unconfirmed_sub"}))
        while True:
            message = await ws.recv()
            data = json.loads(message)
            if data.get("op") == "utx":
                tx = data.get("x")
                total_out = sum(o["value"] for o in tx.get("out", []))
                if total_out >= BTC_THRESHOLD:
                    tx_data = {
                        "TXID": tx["hash"],
                        "Total BTC": total_out / 1e8,
                        "Fee BTC": tx["fee"] / 1e8,
                        "Size": tx["size"],
                        "Time": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(tx["time"]))
                    }
                    # Añadir a tabla
                    tx_table = pd.concat([tx_table, pd.DataFrame([tx_data])], ignore_index=True)
                    placeholder.dataframe(tx_table)

                    if SEND_TO_AIRTABLE:
                        send_to_airtable(tx_data)

# ----------------------------
# Botón para exportar CSV
# ----------------------------
if st.button("Exportar tabla a CSV"):
    csv = tx_table.to_csv(index=False)
    st.download_button(label="Descargar CSV", data=csv, file_name="txs_mempool.csv", mime="text/csv")

# ----------------------------
# Ejecutar la app
# ----------------------------
def main():
    asyncio.run(monitor_mempool())

if __name__ == "__main__":
    main()
