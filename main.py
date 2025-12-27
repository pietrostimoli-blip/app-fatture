import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configurazione Pagina
st.set_page_config(page_title="Gemini Business AI", layout="wide")

# 2. CONFIGURAZIONE LINK GOOGLE (Metti il tuo URL /exec qui)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwceekBx0hRgmfnR5agS7oM81C4OdxY3n3ZxQmv0P-R7v1KAdCnD68TK7ODc-QdPSCo/exec
"

# 3. UTENTI E PASSWORD (Ogni utente avrà il suo foglio nel database)
UTENTI = {
    "admin": "12345",
    "negozio1": "pass1",
    "negozio2": "pass2"
}

# --- SISTEMA DI LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Accesso Gestionale AI")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u in UTENTI and UTENTI[u] == p:
            st.session_state['auth'] = True
            st.session_state['user'] = u
            st.rerun()
        else:
            st.error("Credenziali non valide")
    st.stop()

# --- FUNZIONE ANALISI GEMINI (v1beta) ---
def analizza_con_gemini(file, tipo_doc):
    try:
        if "API_KEY" not in st.secrets:
            st.error("Manca la API_KEY nei Secrets di Streamlit!")
            return None
        
        API_KEY = st.secrets["API_KEY"]
        file_bytes = file.read()
        
        # Prompt per l'estrazione intelligente
        prompt = f"Sei un assistente contabile. Analizza questa fattura di {tipo_doc}. Estrai i seguenti dati separati da virgola: 1.Soggetto (Fornitore/Cliente), 2.DataDocumento, 3.Totale, 4.Imponibile, 5.IVA, 6.Scadenza, 7.Articoli. Rispondi SOLO con i valori."

        # Preparazione dati per Gemini 1.5 Flash
        if file.name.lower().endswith('.xml'):
            testo_xml = file_bytes.decode('utf-8', errors='ignore')
            payload = {"contents": [{"parts": [{"text": f"{prompt}\n\n{testo_xml}"}]}]}
        else:
            b64_file = base64.b64encode(file_bytes).decode()
            payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": file.type, "data": b64_file}}]}]}

        # Endpoint aggiornato a v1beta per supporto totale a Gemini 1.5 Flash
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        res = requests.post(url_api, json=payload).json()
        
        if 'candidates' in res:
            testo_estratto = res['candidates'][0]['content']['parts'][0]['text']
            dati = [i.strip() for i in testo_estratto.split(',')]
            while len(dati) < 7: dati.append("N/D")
            return dati
        else:
            st.error(f"Errore risposta Gemini: {res}")
            return None
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return None

# --- INTERFACCIA PRINCIPALE ---
st.title(f"📊 Dashboard: {st.session_state['user']}")
st.write(f"I dati verranno salvati nel foglio dedicato: **{st.session_state['user']}**")

tab1, tab2 = st.tabs(["📥 ACQUISTI", "📤 VENDITE"])

with tab1:
    up_acq = st.file_uploader("Carica Fattura Acquisto", type=['pdf', 'jpg', 'png', 'xml'], key="u_acq")
    if up_acq and st.button("🔍 ANALIZZA E ARCHIVIA ACQUISTO"):
        with st.spinner("Gemini sta analizzando il documento..."):
            d = analizza_con_gemini(up_acq, "ACQUISTO")
            if d:
                payload = {
                    "utente": st.session_state['user'],
                    "tipo": "ACQUISTO",
                    "soggetto": d[0], "data_doc": d[1], "totale": d[2],
                    "imponibile": d[3], "iva": d[4], "note": f"Articoli: {d[6]}"
                }
                if requests.post(WEBHOOK_URL, json=payload).status_code == 200:
                    st.success(f"Archiviato con successo nel database {st.session_state['user']}!")
                    st.balloons()

with tab2:
    up_ven = st.file_uploader("Carica Fattura Vendita", type=['pdf', 'jpg', 'png', 'xml'], key="u_ven")
    if up_ven and st.button("🔍 ANALIZZA E ARCHIVIA VENDITA"):
        with st.spinner("Gemini sta analizzando la vendita..."):
            d = analizza_con_gemini(up_ven, "VENDITA")
            if d:
                payload = {
                    "utente": st.session_state['user'],
                    "tipo": "VENDITA",
                    "soggetto": d[0], "data_doc": d[1], "totale": d[2],
                    "imponibile": d[3], "iva": d[4], "note": f"Articoli: {d[6]}"
                }
                if requests.post(WEBHOOK_URL, json=payload).status_code == 200:
                    st.success(f"Vendita registrata nel database {st.session_state['user']}!")
                    st.balloons()

if st.sidebar.button("🚪 Logout"):
    st.session_state['auth'] = False
    st.rerun()
