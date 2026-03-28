import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
from twelvedata import TDClient
from streamlit_autorefresh import st_autorefresh

# --- EINSTELLUNGEN ---
# Ersetze 'DEIN_API_KEY' mit dem Key von twelvedata.com
API_KEY = '6c608766b8554cec92e0b9aff8da9a6b' 
SYMBOL = 'BRENT'
INTERVALL = '1min'

st.set_page_config(page_title="Brent Profi-Monitor", page_icon="🛢️")

# Auto-Refresh alle 90 Sekunden (schont das API-Limit des kostenlosen Kontos)
st_autorefresh(interval=90 * 1000, key="oil_update")

def get_professional_data():
    td = TDClient(apikey=API_KEY)
    # Holt die letzten 50 Kerzen für präzise Indikatoren
    ts = td.time_series(
        symbol=SYMBOL,
        interval=INTERVALL,
        outputsize=50,
        exchange="ICE" # Brent wird primär an der ICE gehandelt
    )
    df = ts.as_pandas()
    
    # Twelve Data liefert Daten absteigend (neueste oben), wir brauchen sie aufsteigend
    df = df.sort_index(ascending=True)
    
    # Indikatoren berechnen
    df['SMA_20'] = ta.sma(df['close'], length=20)
    df['RSI'] = ta.rsi(df['close'], length=14)
    return df

st.markdown("<h1 style='text-align: center;'>🛢️ Brent Öl LIVE</h1>", unsafe_allow_html=True)

try:
    data = get_professional_data()
    current_price = data['close'].iloc[-1]
    prev_price = data['close'].iloc[-2]
    rsi = data['RSI'].iloc[-1]
    sma = data['SMA_20'].iloc[-1]
    
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100

    # Hauptanzeige
    st.metric(label=f"Brent Crude ({INTERVALL})", 
              value=f"${current_price:.2f}", 
              delta=f"{change:.2f}$ ({change_pct:.2f}%)")

    # Profi-Logik für Empfehlung
    st.markdown("---")
    
    # Kriterien definieren
    is_uptrend = current_price > sma
    is_oversold = rsi < 35
    is_overbought = rsi > 65

    if is_uptrend and not is_overbought:
        rec, color, explanation = "KAUFEN", "#2ecc71", "Aufwärtstrend bestätigt und noch nicht überkauft."
    elif is_oversold:
        rec, color, explanation = "STARKES KAUFEN", "#27ae60", "Öl ist aktuell stark unterbewertet (RSI)."
    elif not is_uptrend and is_overbought:
        rec, color, explanation = "STARKES VERKAUFEN", "#c0392b", "Abwärtstrend und massiv überkauft."
    elif not is_uptrend:
        rec, color, explanation = "VERKAUFEN", "#e74c3c", "Preis liegt unter dem Trend (SMA20)."
    else:
        rec, color, explanation = "ABWARTEN", "#f1c40f", "Markt ist aktuell unentschlossen."

    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:15px; text-align:center; color:white;">
            <p style="margin:0; font-size:1.2rem;">AKTUELLE EMPFEHLUNG</p>
            <h1 style="margin:0; font-size:3rem; font-weight:bold;">{rec}</h1>
            <p style="margin-top:10px; opacity:0.9;">{explanation}</p>
        </div>
    """, unsafe_allow_html=True)

    # Info-Bereich
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**RSI:** {rsi:.2f}")
    with col2:
        st.info(f"**SMA20:** ${sma:.2f}")

    st.caption(f"Datenquelle: Twelve Data (ICE) | Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.error(f"Fehler: {e}")
    st.info("Prüfe deinen API-Key oder ob die Börse gerade geöffnet hat.")

st.warning("⚠️ Achtung: Trading beinhaltet hohe Risiken. Diese App dient nur zur Information.")
