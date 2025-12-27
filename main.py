import streamlit as st
import requests
import base64
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Gestionale AI Cloud", layout="wide")

# INCOLLA QUI L'URL CHE HAI COPIATO DA APPS SCRIPT
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_APPS_SCRIPT"

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .metric-card { background: #1c2128; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .stButton>button { background-color: #238636; color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    u = st.sidebar.text_input("User")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Accedi"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

st.title("📊 Gestionale AI: Archiviazione Reale")

with st.sidebar:
    file = st.file_uploader("Carica Documento", type=['pdf', 'jpg', 'png'])

if file:
    if st.button("🚀 ANALIZZA E SCRIVI SU GOOGLE SHEETS"):
        try:
            with st.spinner("L'AI sta leggendo e scrivendo sul tuo foglio..."):
                API_KEY = st.secrets["API_KEY"]
                file_b64 = base64.b64encode(file.read()).decode("utf-8")
                
                # Chiamata AI
                url_ai = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                payload_ai = {
                    "contents": [{"parts": [{"text": "Estrai Fornitore, Data, Totale, Imponibile, IVA, Note separati da virgola."},
                                          {"inline_data": {"mime_type": "image/jpeg", "data": file_b64}}]}]
                }
                
                res_ai = requests.post(url_ai, json=payload_ai).json()
                d = [item.strip() for item in res_ai['candidates'][0]['content']['parts'][0]['text'].split(',')]
                
                # INVIO DATI A GOOGLE SHEETS
                dati_per_sheets = {
                    "fornitore": d[0],
                    "data_fattura": d[1],
                    "totale": d[2],
                    "imponibile": d[3],
                    "iva": d[4],
                    "note": d[5] if len(d)>5 else "N/D"
                }
                
                response_sheets = requests.post(WEBHOOK_URL, json=dati_per_sheets)
                
                if response_sheets.status_code == 200:
                    st.success("✅ Dati scritti con successo nel Foglio Google!")
                    st.balloons()
                    # Visualizzazione anteprima
                    st.markdown(f"""
                    <div class="metric-card">
                        <b>Fornitore:</b> {d[0]}<br>
                        <b>Data:</b> {d[1]}<br>
                        <b>Totale:</b> {d[2]} €
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("L'AI ha letto i dati, ma non è riuscita a scriverli nel foglio.")
                    
        except Exception as e:
            st.error(f"Errore: {e}")

st.markdown("---")
st.markdown("🔗 [Vai al tuo Database Google Sheets](https://docs.google.com/spreadsheets/d/13YmESjh6YHVENUwAX1VQPdKPOOULHwv1HU_Y7jOBGn4)")
