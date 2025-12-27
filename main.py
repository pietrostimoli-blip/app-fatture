import streamlit as st
import requests
import base64
import plotly.graph_objects as go

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scanner Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .metric-card { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
    .m-label { color: #8b949e; font-size: 0.8rem; }
    .m-value { color: #58a6ff; font-size: 1.5rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    u = st.sidebar.text_input("User")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Entra"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- APP ---
st.title("📊 Scanner Analitico")

with st.sidebar:
    file = st.file_uploader("Carica file", type=['pdf', 'jpg', 'png'])
    if st.button("🚪 Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    if st.button("🔍 ANALIZZA"):
        try:
            with st.spinner("Interrogazione Google AI..."):
                KEY = st.secrets["API_KEY"]
                file_b64 = base64.b64encode(file.read()).decode("utf-8")
                mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                # Chiamata alla versione stabile
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={KEY}"
                payload = {
                    "contents": [{"parts": [
                        {"text": "Rispondi solo con: Fornitore, Data, Totale, Imponibile, IVA separati da virgola. Usa 0 se mancano."},
                        {"inline_data": {"mime_type": mime, "data": file_b64}}
                    ]}]
                }
                
                response = requests.post(url, json=payload)
                res_data = response.json()
                
                if response.status_code == 200:
                    testo = res_data['candidates'][0]['content']['parts'][0]['text']
                    d = [item.strip() for item in testo.split(',')]
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="metric-card"><div class="m-label">FORNITORE</div><div class="m-value">{d[0]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-card"><div class="m-label">DATA</div><div class="m-value">{d[1]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-card"><div class="m-label">TOTALE</div><div class="m-value">{d[2]} €</div></div>', unsafe_allow_html=True)
                    
                    with c2:
                        imp = float(d[3].replace(',','.'))
                        iva = float(d[4].replace(',','.'))
                        fig = go.Figure(data=[go.Pie(labels=['Netto', 'IVA'], values=[imp, iva], hole=.4)])
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                        st.plotly_chart(fig)
                else:
                    # Questo ti spiega il perché dell'errore
                    st.error(f"Errore Google ({response.status_code}): {res_data['error']['message']}")
                    if "API_KEY_INVALID" in str(res_data):
                        st.warning("La chiave API non è valida. Ricreala in Google AI Studio.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
