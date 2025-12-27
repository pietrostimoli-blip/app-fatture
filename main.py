import streamlit as st
import requests
import base64
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Financial Dashboard", page_icon="📊", layout="wide")

# --- CSS DARK PROFESSIONAL STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .metric-card {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #58a6ff; }
    .m-label { color: #8b949e; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .m-value { color: #58a6ff; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
    .login-box {
        max-width: 420px;
        margin: 100px auto;
        padding: 40px;
        background: #161b22;
        border-radius: 16px;
        border: 1px solid #30363d;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📊 AI Dashboard Login</h2>", unsafe_allow_html=True)
    u = st.text_input("User")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Accesso Negato")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- DASHBOARD ATTIVA ---
st.title("📑 Analisi Fatture & Report AI")
st.markdown(f"Stato Bot: **13.82 USDT** | Diff: :red[**-619.84 USDT**]")

with st.sidebar:
    st.header("📂 Carica File")
    file = st.file_uploader("Trascina PDF o Immagine", type=['pdf', 'jpg', 'jpeg', 'png'])
    st.markdown("---")
    if st.button("🚪 Log Out"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    col_stats, col_graph = st.columns([1, 1])
    
    if st.button("🚀 AVVIA ANALISI PROFONDA"):
        try:
            with st.spinner("L'intelligenza artificiale sta elaborando..."):
                API_KEY = st.secrets["API_KEY"]
                file_data = base64.b64encode(file.read()).decode("utf-8")
                mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                # Chiamata API V1 (Bypass 404)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analizza il documento e restituisci SOLO i valori separati da virgola: Fornitore, Data, Totale (numero), Imponibile (numero), IVA (numero)"},
                            {"inline_data": {"mime_type": mime_type, "data": file_data}}
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data_raw = response.json()['candidates'][0]['content']['parts'][0]['text'].split(',')
                
                # Pulizia dati per il grafico
                fornitore, data_fatt, totale = data_raw[0], data_raw[1], data_raw[2]
                imp_val = float(data_raw[3].strip().replace('€',''))
                iva_val = float(data_raw[4].strip().replace('€',''))

                with col_stats:
                    st.markdown(f"""
                        <div class="metric-card"><div class="m-label">🏢 Fornitore</div><div class="m-value">{fornitore}</div></div>
                        <div class="metric-card" style="margin-top:10px;"><div class="m-label">📅 Data</div><div class="m-value">{data_fatt}</div></div>
                        <div class="metric-card" style="margin-top:10px; border-color: #238636;"><div class="m-label">💰 Totale</div><div class="m-value">{totale} €</div></div>
                    """, unsafe_allow_html=True)

                with col_graph:
                    fig = go.Figure(data=[go.Pie(labels=['Netto (Imponibile)', 'Tasse (IVA)'], 
                                             values=[imp_val, iva_val], 
                                             hole=.4, 
                                             marker_colors=['#58a6ff', '#f85149'])])
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color="white",
                        margin=dict(t=0, b=0, l=0, r=0),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.balloons()
        except Exception as e:
            st.error(f"Errore nell'estrazione: Assicurati che i numeri siano leggibili. ({e})")
else:
    st.info("Carica un documento per visualizzare la dashboard analitica.")
