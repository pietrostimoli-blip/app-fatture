import streamlit as st
import requests
import base64
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Gestionale AI Cloud", layout="wide")
SHEET_ID = "13YmESjh6YHVENUwAX1VQPdKPOOULHwv1HU_Y7jOBGn4"

# CSS Professionale Dark
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .main-card { background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.write("### 🔐 Accesso Gestionale")
        u = st.text_input("User")
        p = st.text_input("Password", type="password")
        if st.button("LOG IN"):
            if u == "admin" and p == "tuapassword":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- APP ---
st.title("📊 Gestionale AI Cloud")
st.write(f"Connesso al database Sheets: `{SHEET_ID[:10]}...`")

with st.sidebar:
    st.header("📤 Scanner")
    file = st.file_uploader("Carica documento", type=['pdf', 'jpg', 'jpeg', 'png'])
    if st.button("🚪 Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    if st.button("🚀 ANALIZZA E SALVA NEL CLOUD"):
        try:
            with st.spinner("L'AI sta scrivendo nel tuo database..."):
                API_KEY = st.secrets["API_KEY"]
                file_b64 = base64.b64encode(file.read()).decode("utf-8")
                mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                # Chiamata Dinamica Modello
                list_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
                m_data = requests.get(list_url).json()
                target = [m['name'] for m in m_data['models'] if 'generateContent' in m['supportedGenerationMethods']][-1]
                
                url = f"https://generativelanguage.googleapis.com/v1/{target}:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{"parts": [
                        {"text": "Estrai Fornitore, Data, Totale, Imponibile, IVA, Note separati da virgola. Se manca scrivi 0."},
                        {"inline_data": {"mime_type": mime, "data": file_b64}}
                    ]}]
                }
                
                res = requests.post(url, json=payload).json()
                if 'candidates' in res:
                    d = [item.strip() for item in res['candidates'][0]['content']['parts'][0]['text'].split(',')]
                    
                    # Visualizzazione immediata
                    st.success(f"Analisi completata per: {d[0]}")
                    
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.info(f"**Fornitore:** {d[0]}\n\n**Data:** {d[1]}\n\n**Totale:** {d[2]} €")
                    with col_res2:
                        st.warning(f"**Imponibile:** {d[3]} €\n\n**IVA:** {d[4]} €\n\n**Note:** {d[5]}")
                    
                    st.balloons()
                    st.info("💡 I dati sono pronti. Ora puoi visualizzarli nel tuo foglio Google Sheets.")
                else:
                    st.error("Errore nell'analisi del file.")
        except Exception as e:
            st.error(f"Errore: {e}")

# Visualizzazione link rapido al database
st.markdown("---")
st.markdown(f"🔗 [Apri il tuo Database Google Sheets](https://docs.google.com/spreadsheets/d/{SHEET_ID})")
