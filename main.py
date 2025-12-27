import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Deve essere la prima istruzione
st.set_page_config(page_title="AI Business Dashboard", layout="wide")

# 2. CONFIGURAZIONE (Sostituisci col tuo link /exec)
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_APPS_SCRIPT"

# 3. LISTA UTENTI (Inserisci qui i tuoi nomi e password)
UTENTI_AUTORIZZATI = {
    "admin": "12345",
    "negozio1": "scelta1",
    "ufficio": "2025"
}

# --- STILE ---
st.markdown("<style>.stApp { background-color: #0d1117; color: #e6edf3; }</style>", unsafe_allow_html=True)

# --- LOGICA DI LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Accesso Gestionale")
    user_in = st.text_input("Username")
    pass_in = st.text_input("Password", type="password")
    
    if st.button("LOG IN"):
        # Controllo diretto e pulito
        if user_in in UTENTI_AUTORIZZATI and UTENTI_AUTORIZZATI[user_in] == pass_in:
            st.session_state['auth'] = True
            st.session_state['user_loggato'] = user_in
            st.success("Accesso eseguito! Ricaricando...")
            st.rerun()
        else:
            st.error("Credenziali non valide. Riprova.")
    st.stop()

# --- DA QUI IN POI L'APP DOPO IL LOGIN ---
st.title(f"📊 Benvenuto {st.session_state['user_loggato']}")
st.write("Gestionale Cloud Attivo")

# Menu rapido
tab1, tab2 = st.tabs(["📥 Acquisti", "📤 Vendite"])

with tab1:
    st.subheader("Carica Fattura Acquisto")
    file_acq = st.file_uploader("Scegli file", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'])
    if file_acq and st.button("Analizza"):
        st.info("Analisi in corso... (Verifica API KEY nei Secrets)")
        # ... resto della logica di analisi ...

with tab2:
    st.subheader("Registra Vendita")
    # ... resto della logica di vendita ...

if st.sidebar.button("🚪 Logout"):
    st.session_state['auth'] = False
    st.rerun()
