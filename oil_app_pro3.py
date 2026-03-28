import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

# Konfiguration für die Smartphone-Ansicht
st.set_page_config(page_title="Brent Öl Future", page_icon="🛢️", layout="centered")

# Automatischer Refresh alle 60 Sekunden (schont Datenvolumen am Handy)
st_autorefresh(interval=60 * 1000, key="oil_update")

def get_oil_data():
    # BZ=F ist der exakte Ticker für den ICE Brent Crude Oil Future (EB)
    df = yf.download("BZ=F", period="5d", interval="15m", progress=False)
    
    # Technische Indikatoren für die Empfehlung
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

st.markdown("<h2 style='text-align: center;'>🛢️ Brent Oil Future (EB)</h2>", unsafe_allow_html=True)

try:
    data = get_oil_data()
    
    # Aktuelle Werte extrahieren
    current_price = float(data['Close'].iloc[-1])
    prev_close = float(data['Close'].iloc[-2])
    rsi = float(data['RSI'].iloc[-1])
    sma = float(data['SMA_20'].iloc[-1])
    
    # Kursänderung berechnen
    change = current_price - prev_close
    change_pct = (change / prev_close) * 100

    # Große Anzeige für das Smartphone
    st.metric(label="Aktueller Kurs (USD)", 
              value=f"${current_price:.2f}", 
              delta=f"{change:.2f}$ ({change_pct:.2f}%)")

    st.markdown("---")

    # --- EMPFEHLUNGS-LOGIK ---
    # KAUFEN: Preis über dem Trend (SMA) und RSI hat noch Luft nach oben
    # VERKAUFEN: Preis unter dem Trend (SMA) ODER RSI ist zu hoch (überkauft)
    
    if current_price > sma and rsi < 65:
        rec, color, desc = "KAUFEN", "#2ecc71", "Aufwärtstrend bestätigt."
    elif rsi < 30:
        rec, color, desc = "STARKES KAUFEN", "#27ae60", "Öl ist überverkauft (RSI)."
    elif current_price < sma or rsi > 70:
        rec, color, desc = "VERKAUFEN", "#e74c3c", "Trendwende oder überkauft."
    else:
        rec, color, desc = "NEUTRAL", "#f1c40f", "Abwarten auf Signal."

    # Große Empfehlungsbox
    st.markdown(f"""
        <div style="background-color:{color}; padding:25px; border-radius:15px; text-align:center; color:white;">
            <p style="margin:0; font-size:1.2rem; font-weight:lighter;">EMPFEHLUNG</p>
            <h1 style="margin:0; font-size:3.5rem; font-weight:bold;">{rec}</h1>
            <p style="margin-top:10px; opacity:0.9;">{desc}</p>
        </div>
    """, unsafe_allow_html=True)

    # Details im unteren Bereich
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**RSI (14):** {rsi:.2f}")
    with col2:
        st.write(f"**SMA (20):** ${sma:.2f}")

    st.caption(f"Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.warning("Suche Marktdaten... (Börse evtl. geschlossen?)")
    st.info("Hinweis: Brent Öl wird an der ICE gehandelt. Am Wochenende sind die Kurse stabil.")

st.markdown("---")
st.caption("Trading-Hinweis: Diese App dient nur zur Information und nutzt verzögerte Marktdaten.")