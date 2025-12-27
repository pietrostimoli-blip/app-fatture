import streamlit as st
import requests
import base64
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Scanner Professionale", page_icon="📊", layout="wide")

# --- CSS TOTAL DARK ---
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
        margin-bottom: 15px;
    }
    .m-label { color: #8b949e; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .m-value { color: #58a6ff; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
    .login-box {
        max-width: 420px;
        margin: 100px auto;
        padding: 40px;
        background: #161b22;
        border-radius: 16px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📑 Area Riservata</h2>", unsafe_allow_html=True)
    u = st.text_input("User")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Dati errati")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACCIA ---
st.title("📊 Dashboard Analisi Documenti")
st.markdown("---")

with st.sidebar:
    st.header("📂 Caricamento")
    file = st.file_uploader("Scegli un file", type=['pdf', 'jpg', 'jpeg', 'png'])
    if st.button("🚪 Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    col_left, col_right = st.columns([1, 1])
    if st.button("🚀 AVVIA ANALISI"):
        try:
            with st.spinner("Analisi AI in corso..."):
                API_KEY = st.secrets["API_KEY"]
                file_bytes = file.read()
                file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{"parts": [
                        {"text": "Estrai Fornitore, Data, Totale, Imponibile, IVA separati da virgola. Se non trovi un dato scrivi '0'."},
                        {"inline_data": {"mime_type": mime, "data": file_b64}}
                    ]}]
                }
                
                res = requests.post(url, json=payload).json()
                
                if 'candidates' in res and len(res['candidates']) > 0:
                    testo = res['candidates'][0]['content']['parts'][0]['text']
                    d = [item.strip() for item in testo.split(',')]
                    while len(d) < 5: d.append("0")

                    with col_left:
                        st.markdown(f'<div class="metric-card"><div class="m-label">Fornitore</div><div class="m-value">{d[0]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-card"><div class="m-label">Data</div><div class="m-value">{d[1]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-card" style="border-color: #238636;"><div class="m-label">Totale</div><div class="m-value">{d[2]} €</div></div>', unsafe_allow_html=True)

                    with col_right:
                        try:
                            # Pulizia stringhe per conversione numerica
                            v_imp = float(d[3].replace('€','').replace(',','.').strip())
                            v_iva = float(d[4].replace('€','').replace(',','.').strip())
                            
                            fig = go.Figure(data=[go.Pie(labels=['Netto', 'IVA'], values=[v_imp, v_iva], hole=.4, marker_colors=['#58a6ff', '#f85149'])])
                            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True, margin=dict(t=0,b=0,l=0,r=0))
                            st.plotly_chart(fig, use_container_width=True)
                        except:
                            st.warning("Dati numerici non sufficienti per il grafico.")
                else:
                    st.error("Errore: L'AI non ha risposto. Controlla l'API KEY.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
else:
    st.info("Carica un documento per iniziare.")
