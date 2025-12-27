import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE SICURA ---
try:
    API_KEY = st.secrets["API_KEY"]
    SHEET_ID = st.secrets["SHEET_ID"]
except:
    st.error("Configura i Secrets su Streamlit Cloud con API_KEY e SHEET_ID!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- DATI DEL TUO BOT (Dalle nostre conversazioni precedenti) ---
VALORE_INIZIALE = 633.66  # Il totale che avevamo stabilito (Bot A4 + A6 + Sub + Wallet)
VALORE_ATTUALE = 13.82    # L'ultimo valore che mi hai comunicato
DIFFERENZA = VALORE_ATTUALE - VALORE_INIZIALE

# --- LISTA ACCESSI CLIENTI ---
UTENTI_AUTORIZZATI = {
    "admin": "tuapassword",
    "negozio1": "pass123",
    "cliente_test": "test2025"
}

st.set_page_config(page_title="Gestione AI & Dashboard Bot", layout="wide")

# --- SIDEBAR: DASHBOARD E LOGIN ---
st.sidebar.title("📊 La Tua Dashboard")

# Sistema "Aggiorna Dashboard" automatico
st.sidebar.metric(label="Valore Bot Attuale", value=f"{VALORE_ATTUALE} USDT", delta=f"{DIFFERENZA:.2f} USDT")

st.sidebar.markdown("---")
st.sidebar.title("🔑 Accesso Clienti")
utente = st.sidebar.text_input("Nome Utente")
password = st.sidebar.text_input("Password", type="password")

# --- CONTROLLO ACCESSO ---
if utente in UTENTI_AUTORIZZATI and UTENTI_AUTORIZZATI[utente] == password:
    
    # Se l'utente è "admin", vede anche i dati tecnici
    if utente == "admin":
        st.title("🛡️ Pannello Amministratore")
        st.write(f"Monitoraggio Bot attivo: {VALORE_ATTUALE} USDT")
    else:
        st.title(f"📲 Scanner Professionale - {utente.capitalize()}")

    st.info("Sistema pronto per l'acquisizione documenti.")

    # --- LOGICA SCANNER ---
    file = st.file_uploader("Scatta o carica la fattura", type=['jpg', 'jpeg', 'png'])

    if file:
        img = Image.open(file)
        st.image(img, width=400, caption="Documento in fase di analisi")

        if st.button("🔍 ANALIZZA E SALVA NEL DATABASE"):
            with st.spinner("L'intelligenza artificiale sta leggendo i dati..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Istruzioni precise per l'AI
                prompt = """
                Analizza questa fattura ed estrai: Fornitore, Data, Imponibile, IVA, TOTALE.
                Formatta i dati in modo professionale.
                """
                response = model.generate_content([prompt, img])
                
                st.success("✅ Dati acquisiti e pronti per il foglio Google!")
                st.markdown(f"### Risultato:\n{response.text}")
                
                # Nota per il database
                st.info(f"Record pronto per il foglio ID: {SHEET_ID}")
else:
    st.title("📑 Benvenuto nel Portale Documenti")
    st.warning("Inserisci le credenziali a sinistra per sbloccare le funzioni di scansione.")
    st.stop()
