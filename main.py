import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURAZIONE SICURA (Dati dai Secrets di Streamlit)
try:
    API_KEY = st.secrets["API_KEY"]
    # Usiamo il modello corretto con il prefisso 'models/' per evitare il 404
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Errore: API_KEY non configurata nei Secrets di Streamlit!")
    st.stop()

# 2. GESTIONE ACCESSI (Aggiungi qui i tuoi clienti)
UTENTI = {
    "admin": "tuapassword",
    "negozio1": "pass123",
    "cliente_test": "test2025"
}

st.set_page_config(page_title="Scanner Professionale AI", layout="centered")

# Inizializzazione sessione di login
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

# --- APP LIVE (Visibile solo dopo il Login) ---
st.title("📑 Scanner Fatture Professionale")
st.write(f"Connesso come: **{st.session_state['user_attuale'].capitalize()}**")

file = st.file_uploader("Carica o scatta una foto", type=['jpg', 'jpeg', 'png'])

if file:
    img = Image.open(file)
    st.image(img, caption="Documento caricato", use_container_width=True)
    
    if st.button("🔍 ANALIZZA DOCUMENTO"):
        try:
            with st.spinner("L'intelligenza artificiale sta leggendo i dati..."):
                # Specifichiamo il modello nel formato corretto
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                
                prompt = "Analizza questa immagine e restituisci: Fornitore, Data e Totale in modo chiaro."
                response = model.generate_content([prompt, img])
                
                st.success("✅ Analisi completata!")
                st.subheader("Dati Estratti:")
                st.write(response.text)
                
                st.balloons()
        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")
            st.info("Verifica che la tua API KEY sia attiva e corretta.")
