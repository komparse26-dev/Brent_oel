import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# Konfiguration für Smartphone-Ansicht
st.set_page_config(page_title="Öl-Ticker", page_icon="🛢️", layout="centered")

# Automatischer Refresh alle 60 Sekunden
st_autorefresh(interval=60 * 1000, key="datarefresh")

def get_data():
    # Brent Öl Daten (BZ=F)
    df = yf.download("BZ=F", period="1d", interval="5m", progress=False)
    
    # Technische Indikatoren berechnen
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

st.markdown("<h1 style='text-align: center;'>🛢️ Brent Öl Live</h1>", unsafe_allow_html=True)

try:
    data = get_data()
    current_price = data['Close'].iloc[-1]
    last_price = data['Close'].iloc[-2]
    rsi = data['RSI'].iloc[-1]
    sma = data['SMA_20'].iloc[-1]
    change = current_price - last_price
    change_pct = (change / last_price) * 100

    # Preis-Anzeige (Groß für Handy)
    st.metric(label="Brent Crude (USD)", value=f"${current_price:.2f}", delta=f"{change_pct:.2f}%")

    # Logik für Empfehlung
    # KAUFEN: RSI niedrig (überverkauft) UND Preis über SMA
    # VERKAUFEN: RSI hoch (überkauft) ODER Preis unter SMA
    
    st.markdown("---")
    if rsi < 40 and current_price > sma:
        rec = "STARKES KAUFEN"
        color = "#2ecc71" # Grün
    elif current_price > sma:
        rec = "HALTEN / KAUFEN"
        color = "#27ae60"
    elif rsi > 65 or current_price < sma:
        rec = "VERKAUFEN"
        color = "#e74c3c" # Rot
    else:
        rec = "NEUTRAL"
        color = "#f1c40f" # Gelb

    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:15px; text-align:center;">
            <h2 style="color:white; margin:0;">EMPFEHLUNG:</h2>
            <h1 style="color:white; margin:0; font-size:40px;">{rec}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Details für Profis
    st.write("")
    col1, col2 = st.columns(2)
    col1.write(f"**RSI (14):** {rsi:.2f}")
    col2.write(f"**Trend (SMA20):** {'Aufwärts' if current_price > sma else 'Abwärts'}")

    st.caption(f"Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.error("Warten auf Marktdaten...")
    st.caption("Hinweis: Am Wochenende pausiert der Öl-Handel.")

st.info("💡 Tipp: Füge diese Seite zum Home-Bildschirm deines Handys hinzu!")