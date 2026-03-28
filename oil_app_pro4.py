import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="Brent Live", page_icon="🛢️", layout="centered")

# CSS für echtes Smartphone-Design
st.markdown("""
    <style>
    /* Hintergrund & App-Feeling */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: white;
    }
    /* Streamlit-Header & Footer ausblenden */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Preis-Design */
    [data-testid="stMetricValue"] {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    
    /* Karten-Design für Empfehlungen */
    .trade-card {
        padding: 30px;
        border-radius: 25px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .status-dot {
        height: 12px;
        width: 12px;
        background-color: #2ecc71;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    .info-box {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 15px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Auto-Refresh alle 60 Sekunden
st_autorefresh(interval=60 * 1000, key="oil_update")

@st.cache_data(ttl=60)
def get_data():
    try:
        # BZ=F ist Brent Oil Future
        df = yf.download("BZ=F", period="5d", interval="15m", progress=False)
        if df.empty: return None
        # Korrektur der Spaltennamen (yfinance V3 Fix)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df['SMA'] = ta.sma(df['Close'], length=20)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df
    except:
        return None

# --- UI START ---
st.markdown(f"<div style='text-align: center; margin-top: -50px;'><p style='color: #888; margin-bottom: 0;'>BRENT OIL FUTURE</p></div>", unsafe_allow_html=True)

try:
    df = get_data()
    if df is not None:
        cur = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        sma = float(df['SMA'].iloc[-1])
        rsi = float(df['RSI'].iloc[-1])
        
        change = cur - prev
        
        # Metrik Anzeige
        st.metric(label="", value=f"${cur:.2f}", delta=f"{change:.2f}$")

        # Logik & Farben
        if cur > sma and rsi < 65:
            res, color, bg = "KAUFEN", "#2ecc71", "rgba(46, 204, 113, 0.2)"
            icon = "📈"
        elif cur < sma or rsi > 70:
            res, color, bg = "VERKAUFEN", "#e74c3c", "rgba(231, 76, 60, 0.2)"
            icon = "📉"
        else:
            res, color, bg = "NEUTRAL", "#f1c40f", "rgba(241, 196, 15, 0.2)"
            icon = "⚖️"

        # Empfehlungs-Karte
        st.markdown(f"""
            <div class="trade-card" style="background-color: {bg}; border: 1px solid {color};">
                <p style="color: {color}; font-size: 1.2rem; font-weight: bold; margin: 0;">{icon} EMPFEHLUNG</p>
                <h1 style="color: {color}; font-size: 3.1rem; margin: 0;">{res}</h1>
            </div>
        """, unsafe_allow_html=True)

        # Zusätzliche Info-Leiste
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='info-box'><p style='color:#888; font-size:0.8rem; margin:0;'>RSI (14)</p><h3 style='margin:0;'>{rsi:.1f}</h3></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='info-box'><p style='color:#888; font-size:0.8rem; margin:0;'>Trend (20)</p><h3 style='margin:0;'>{('UP' if cur > sma else 'DOWN')}</h3></div>", unsafe_allow_html=True)
            
    else:
        st.error("Daten konnten nicht geladen werden.")

except Exception as e:
    st.info("Markt geschlossen oder lädt...")

# Footer mit pulsierendem Live-Punkt
st.markdown(f"""
    <div style='text-align: center; margin-top: 30px;'>
        <p style='color: #555; font-size: 0.8rem;'>
            <span class="status-dot"></span> LIVE TICKER • {datetime.now().strftime('%H:%M:%S')}
        </p>
    </div>
""", unsafe_allow_html=True)
