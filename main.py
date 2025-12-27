import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configurazione Sicura (NON TOCCARE)
try:
    # Cerchiamo le chiavi nei Secrets di Streamlit
    CHIAVE_AI = st.secrets["API_KEY"]
    genai.configure(api_key=CHIAVE_AI)
except Exception:
    st.error("Errore critico: API_KEY non trovata nei Secrets di Streamlit!")
    st.stop()

# 2. Gestione Accessi (Username: Password)
# PUOI AGGIUNGERE O TOGLIERE UTENTI QUI SOTTO
UTENTI = {
    "admin": "tuapassword",
    "negozio1": "pass123"
}

st.set_page_config(page_title="Scanner Professionale", layout="centered")

# --- BLOCCO DI SICUREZZA ---
if 'autenticato' not in st.session_state:
    st.session_state['autenticato'] = False

# Sidebar per il Login
st.sidebar.title("🔐 Accesso Riservato")
user = st.sidebar.text_input("Utente")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Entra"):
    if user in UTENTI and UTENTI[user] == password:
        st.session_state['autenticato'] = True
    else:
        st.sidebar.error("Credenziali errate")

# Se NON è autenticato, l'app si ferma qui e non mostra NULLA
if not st.session_state['autenticato']:
    st.title("📲 Benvenuto")
    st.info("Inserisci le credenziali nella barra a sinistra per accedere allo scanner.")
    st.stop()

# --- DA QUI IN POI VEDE SOLO CHI HA LA PASSWORD ---
st.title("📑 Scanner Fatture Professionale")

file = st.file_uploader("Scatta o carica una foto", type=['jpg', 'jpeg', 'png'])

if file:
    img = Image.open(file)
    st.image(img, width=400)
    
    if st.button("🔍 ANALIZZA DOCUMENTO"):
        try:
            with st.spinner("L'intelligenza artificiale sta leggendo..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                # Prompt pulito per evitare errori
                response = model.generate_content(["Estrai fornitore, data e totale", img])
                st.success("Analisi Completata!")
                st.write(response.text)
        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")
