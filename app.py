import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Transacciones Bitcoin >0.03 BTC", layout="wide")
st.title("Transacciones Bitcoin superiores a 0,03 BTC (últimas 24h)")

# Umbral en BTC
umbral_btc = 0.03

# Función para obtener transacciones de los últimos 24h
def obtener_transacciones():
    url = "https://blockstream.info/api/mempool/recent"
    try:
        response = requests.get(url)
        response.raise_for_status()
        datos = response.json()

        transacciones = []
        ahora = datetime.utcnow()
        hace_24h = ahora - timedelta(days=1)

        for tx in datos:
            total_sats = sum([out["value"] for out in tx["vout"]])
            total_btc = total_sats / 1e8  # convertir satoshis a BTC
            timestamp = datetime.utcfromtimestamp(tx.get("status", {}).get("block_time", ahora.timestamp()))

            # Filtrar por última 24h y por umbral
            if total_btc >= umbral_btc and timestamp >= hace_24h:
                transacciones.append({
                    "TXID": tx["txid"],
                    "Monto (BTC)": total_btc,
                    "Hora UTC": timestamp
                })

        if not transacciones:
            st.info("No hay transacciones que superen el umbral en las últimas 24 horas.")
            return pd.DataFrame()  # DataFrame vacío
        else:
            df = pd.DataFrame(transacciones)
            df.sort_values("Monto (BTC)", ascending=False, inplace=True)
            return df

    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

# Botón para actualizar
if st.button("Actualizar ahora"):
    df_transacciones = obtener_transacciones()
    if not df_transacciones.empty:
        st.dataframe(df_transacciones, use_container_width=True)
else:
    # Mostrar al cargar la app
    df_transacciones = obtener_transacciones()
    if not df_transacciones.empty:
        st.dataframe(df_transacciones, use_container_width=True)
