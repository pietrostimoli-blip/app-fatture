import streamlit as st
import requests
import base64
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Gestionale AI Pro", layout="wide")

# 🔴 ATTENZIONE: Incolla qui l'URL della tua "Applicazione Web" di Google Apps Script
# Deve finire con /exec
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_GOOGLE_APPS_SCRIPT"

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
        if u == "admin" and p == "12345":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

st.title("📊 Gestionale AI: Archiviazione Reale")

with st.sidebar:
    file = st.file_uploader("Carica Documento (PDF, JPG, PNG)", type=['pdf', 'jpg', 'jpeg', 'png'])

if file:
    # Mostra l'anteprima se è un'immagine
    if file.type != "application/pdf":
        st.image(file, caption="Documento caricato", width=300)

    if st.button("🚀 ANALIZZA E SCRIVI SU GOOGLE SHEETS"):
        try:
            with st.spinner("Analisi e salvataggio in corso..."):
                API_KEY = st.secrets["API_KEY"]
                file_bytes = file.read()
                file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                
                # Rilevamento automatico del tipo di file (JPEG, PNG o PDF)
                mime_type = file.type
                
                # 1. Chiamata AI
                url_ai = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                payload_ai = {
                    "contents": [{
                        "parts": [
                            {"text": "Analizza il documento e restituisci SOLO Fornitore, Data, Totale, Imponibile, IVA, Note separati da virgola. Se un dato manca scrivi 0."},
                            {"inline_data": {"mime_type": mime_type, "data": file_b64}}
                        ]
                    }]
                }
                
                res_ai = requests.post(url_ai, json=payload_ai).json()
                
                if 'candidates' in res_ai:
                    testo_estratto = res_ai['candidates'][0]['content']['parts'][0]['text']
                    d = [item.strip() for item in testo_estratto.split(',')]
                    
                    # Assicuriamoci di avere 6 elementi
                    while len(d) < 6: d.append("0")
                    
                    # 2. INVIO DATI A GOOGLE SHEETS (Tramite l'URL Web App)
                    dati_per_sheets = {
                        "fornitore": d[0],
                        "data_fattura": d[1],
                        "totale": d[2],
                        "imponibile": d[3],
                        "iva": d[4],
                        "note": d[5]
                    }
                    
                    # Inviamo i dati come JSON
                    response_sheets = requests.post(WEBHOOK_URL, json=dati_per_sheets)
                    
                    if response_sheets.status_code == 200:
                        st.success("✅ Dati inviati e scritti su Google Sheets!")
                        st.balloons()
                        st.markdown(f"**Ultimo inserimento:** {d[0]} - {d[2]} €")
                    else:
                        st.error(f"Errore di scrittura su Sheets. Risposta server: {response_sheets.status_code}")
                        st.info("Verifica di aver impostato 'Chiunque' nella distribuzione dello script di Google.")
                else:
                    st.error("L'AI non ha riconosciuto il documento. Prova con una foto più chiara.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {e}")

st.markdown("---")
st.markdown(f"🔗 [Apri il tuo Database Google Sheets](https://docs.google.com/spreadsheets/d/13YmESjh6YHVENUwAX1VQPdKPOOULHwv1HU_Y7jOBGn4)")
