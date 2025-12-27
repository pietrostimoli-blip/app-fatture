import streamlit as st
import requests
import base64
import pandas as pd
import plotly.graph_objects as go

# --- FORZATURA TEMA DARK ---
st.set_page_config(page_title="AI Dashboard Pro", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    /* Sfondo Blu Notte Profondo */
    .stApp {
        background-color: #0b0e14;
        color: #e6edf3;
    }
    /* Card laterale e principale */
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    /* Card dei Risultati (Metriche) */
    .metric-container {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
    }
    .m-label { color: #8b949e; font-size: 14px; text-transform: uppercase; margin-bottom: 5px; }
    .m-value { color: #58a6ff; font-size: 26px; font-weight: bold; }
    
    /* Box Login */
    .login-box {
        max-width: 450px;
        margin: 80px auto;
        background: #1c2128;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAZIONE API ---
API_KEY = st.secrets.get("API_KEY")

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 ACCESSO DASHBOARD</h2>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("LOG IN"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD ATTIVA ---
st.title("📊 Dashboard Analisi Fatture AI")
st.markdown(f"**Benvenuto, Admin** | Valore Bot: `13.82 USDT` | Diff: `-619.84 USDT`")

with st.sidebar:
    st.header("📂 Upload")
    file = st.file_uploader("Carica PDF o Immagine", type=['pdf', 'jpg', 'jpeg', 'png'])
    st.markdown("---")
    if st.button("🚪 Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        if st.button("🚀 AVVIA ANALISI PRO"):
            try:
                with st.spinner("L'AI sta scansionando il documento..."):
                    # Chiamata API V1
                    file_data = base64.b64encode(file.read()).decode("utf-8")
                    mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                    
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": "Analizza e rispondi solo in questo ordine separato da virgola: Nome Fornitore, Data, Totale Euro (solo numero), Imponibile (solo numero), IVA (solo numero)"},
                                {"inline_data": {"mime_type": mime_type, "data": file_data}}
                            ]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    dati = response.json()['candidates'][0]['content']['parts'][0]['text'].split(',')

                    # Visualizzazione Card in alto
                    c1, c2, c3 = st.columns(3)
                    with c1: st.markdown(f'<div class="metric-container"><div class="m-label">Fornitore</div><div class="m-value">{dati[0]}</div></div>', unsafe_allow_html=True)
                    with c2: st.markdown(f'<div class="metric-container"><div class="m-label">Data</div><div class="m-value">{dati[1]}</div></div>', unsafe_allow_html=True)
                    with c3: st.markdown(f'<div class="metric-container"><div class="m-label">Totale</div><div class="m-value">{dati[2]} €</div></div>', unsafe_allow_html=True)

                    # Grafico
                    st.markdown("### 📈 Ripartizione Costi")
                    imp = float(dati[3].replace('€','').strip())
                    iva = float(dati[4].replace('€','').strip())
                    fig = go.Figure(data=[go.Pie(labels=['Imponibile', 'IVA'], values=[imp, iva], hole=.4, marker_colors=['#58a6ff', '#f85149'])])
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig)
            except Exception as e:
                st.error(f"Errore: {e}")
