import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
from streamlit_autorefresh import st_autorefresh

# --- KONFIGURATION ---
# Das Symbol "BZ=F" entspricht dem Brent Oil Future (EB)
SYMBOL = "BZ=F" 
TELEGRAM_TOKEN = 'DEIN_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'DEINE_CHAT_ID'

st.set_page_config(page_title="Brent Future EB Monitor", page_icon="🛢️")

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60 * 1000, key="oil_update")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        pass

def get_data():
    # Wir holen die Daten für Brent Oil Future (EB)
    df = yf.download(SYMBOL, period="5d", interval="15m", progress=False)
    
    # Technische Indikatoren berechnen
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    return df

st.markdown("<h1 style='text-align: center;'>🛢️ Brent Oil Future (EB)</h1>", unsafe_allow_html=True)

try:
    data = get_data()
    # Letzte Zeile extrahieren
    current_price = float(data['Close'].iloc[-1])
    prev_price = float(data['Close'].iloc[-2])
    rsi = float(data['RSI'].iloc[-1])
    sma = float(data['SMA_20'].iloc[-1])
    
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100

    # Anzeige
    st.metric(label="Brent Future EB (USD)", 
              value=f"${current_price:.2f}", 
              delta=f"{change:.2f}$ ({change_pct:.2f}%)")

    # Entscheidungslogik
    st.markdown("---")
    if current_price > sma and rsi < 65:
        rec, color = "KAUFEN", "#2ecc71"
    elif current_price < sma or rsi > 70:
        rec, color = "VERKAUFEN", "#e74c3c"
    else:
        rec, color = "ABWARTEN", "#f1c40f"

    # Push-Logik
    if 'last_rec' not in st.session_state:
        st.session_state.last_rec = rec

    if rec != st.session_state.last_rec:
        msg = f"🚨 BRENT UPDATE: {rec}\nPreis: ${current_price:.2f}\nRSI: {rsi:.2f}"
        send_telegram_msg(msg)
        st.session_state.last_rec = rec

    st.markdown(f"""
        <div style="background-color:{color}; padding:20px; border-radius:15px; text-align:center; color:white;">
            <h1 style="margin:0; font-size:3rem;">{rec}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Info-Werte
    st.write("")
    c1, c2 = st.columns(2)
    c1.info(f"**RSI:** {rsi:.2f}")
    c2.info(f"**Trend (SMA20):** ${sma:.2f}")

except Exception as e:
    st.error("Warten auf Marktdaten...")
    st.info("Hinweis: Brent Futures werden fast rund um die Uhr gehandelt, außer am Wochenende.")

st.caption(f"Letztes Update: {pd.Timestamp.now().strftime('%H:%M:%S')} (Ticker: {SYMBOL})")