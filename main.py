import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Business Dashboard", layout="wide")

# 2. CONFIGURAZIONE LINK GOOGLE (Recuperalo da Apps Script)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwceekBx0hRgmfnR5agS7oM81C4OdxY3n3ZxQmv0P-R7v1KAdCnD68TK7ODc-QdPSCo/exec"

# 3. LISTA UTENTI AUTORIZZATI
UTENTI_AUTORIZZATI = {
    "admin": "12345",
    "ufficio": "2025"
}

# --- SISTEMA DI LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Accesso Gestionale")
    user_in = st.text_input("Username")
    pass_in = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if user_in in UTENTI_AUTORIZZATI and UTENTI_AUTORIZZATI[user_in] == pass_in:
            st.session_state['auth'] = True
            st.session_state['user_attivo'] = user_in
            st.rerun()
    st.stop()

# --- FUNZIONE ANALISI AI ---
def analizza_documento(file, tipo_doc):
    try:
        if "API_KEY" not in st.secrets:
            st.error("Manca API_KEY nei Secrets!")
            return None
        
        API_KEY = st.secrets["API_KEY"]
        file_bytes = file.read()
        prompt = f"Analizza fattura di {tipo_doc}. Estrai: 1.Soggetto, 2.DataDoc, 3.Totale, 4.Imponibile, 5.IVA, 6.Scadenza, 7.Articoli. Rispondi solo con i valori separati da virgola."
        
        if file.name.lower().endswith('.xml'):
            payload = {"contents": [{"parts": [{"text": f"{prompt}\n\n{file_bytes.decode('utf-8')}"}]}]}
        else:
            file_b64 = base64.b64encode(file_bytes).decode("utf-8")
            payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": file.type, "data": file_b64}}]}]}
        
        res = requests.post(f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}", json=payload).json()
        if 'candidates' in res:
            return [item.strip() for item in res['candidates'][0]['content']['parts'][0]['text'].split(',')]
        return None
    except Exception as e:
        st.error(f"Errore AI: {e}")
        return None

# --- INTERFACCIA ---
st.title(f"📊 Dashboard: {st.session_state['user_attivo']}")
tab1, tab2 = st.tabs(["📥 ACQUISTI", "📤 VENDITE"])

with tab1:
    file_acq = st.file_uploader("Carica Acquisto", type=['pdf', 'jpg', 'png', 'xml'], key="acq")
    if file_acq and st.button("🔍 ANALIZZA ACQUISTO"):
        d = analizza_documento(file_acq, "ACQUISTO")
        if d:
            p = {"tipo": "ACQUISTO", "soggetto": d[0], "data_doc": d[1], "totale": d[2], "imponibile": d[3], "iva": d[4], "scadenza": d[5], "note": d[6]}
            requests.post(WEBHOOK_URL, json=p)
            st.success("Archiviato!")

with tab2:
    file_ven = st.file_uploader("Carica Vendita", type=['pdf', 'jpg', 'png', 'xml'], key="ven")
    if file_ven and st.button("🔍 ANALIZZA VENDITA"):
        d = analizza_documento(file_ven, "VENDITA")
        if d:
            p = {"tipo": "VENDITA", "soggetto": d[0], "data_doc": d[1], "totale": d[2], "imponibile": d[3], "iva": d[4], "scadenza": d[5], "note": d[6]}
            requests.post(WEBHOOK_URL, json=p)
            st.success("Archiviato!")


