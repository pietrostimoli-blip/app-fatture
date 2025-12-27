Certamente, ecco il codice completo e "blindato". Ho usato il modello gemini-1.5-flash che è il più veloce e compatibile, strutturando il comando in modo che non cerchi versioni "beta" che danno errore.

Copia tutto questo e sostituisci il contenuto di main.py su GitHub:

Python

import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURAZIONE SICURA
# Recupera la chiave dai Secrets di Streamlit
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Errore: API_KEY non configurata nei Secrets di Streamlit!")
    st.stop()

# 2. GESTIONE ACCESSI (Username: Password)
UTENTI = {
    "admin": "tuapassword",
    "negozio1": "pass123",
    "cliente_test": "test2025"
}

st.set_page_config(page_title="Scanner Professionale AI", layout="centered")

# Inizializzazione sessione
if 'autenticato' not in st.session_state:
    st.session_state['autenticato'] = False

# --- SIDEBAR LOGIN ---
st.sidebar.title("🔐 Area Riservata")
user = st.sidebar.text_input("Utente")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Accedi"):
    if user in UTENTI and UTENTI[user] == password:
        st.session_state['autenticato'] = True
        st.session_state['user_attuale'] = user
        st.rerun()
    else:
        st.sidebar.error("Credenziali non valide")

# --- CONTROLLO ACCESSO ---
if not st.session_state['autenticato']:
    st.title("📲 Portale Documenti AI")
    st.info("Inserisci le tue credenziali a sinistra per iniziare.")
    st.stop()

# --- APP LIVE (Solo dopo il Login) ---
st.title("📑 Scanner Fatture Professionale")
st.write(f"Utente attivo: **{st.session_state['user_attuale'].capitalize()}**")

file = st.file_uploader("Carica o scatta una foto", type=['jpg', 'jpeg', 'png'])

if file:
    img = Image.open(file)
    st.image(img, caption="Documento pronto", use_container_width=True)
    
    if st.button("🔍 ANALIZZA DOCUMENTO"):
        try:
            with st.spinner("L'intelligenza artificiale sta leggendo..."):
                # Utilizzo del modello standard 1.5-flash
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt semplificato per massima compatibilità
                prompt = "Analizza questa immagine. Estrai e scrivi solo: Fornitore, Data e Totale."
                response = model.generate_content([prompt, img])
                
                if response:
                    st.success("✅ Analisi completata!")
                    st.subheader("Dati Estratti:")
                    st.write(response.text)
                    st.balloons()
                else:
                    st.error("L'AI non ha restituito dati. Riprova con una foto più chiara.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
            st.info("Se l'errore persiste (404), crea una NUOVA API KEY su Google
