import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURAZIONE SICURA
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Errore: API_KEY non configurata nei Secrets!")
    st.stop()

# 2. GESTIONE ACCESSI
UTENTI = {
    "admin": "tuapassword",
    "negozio1": "pass123"
}

st.set_page_config(page_title="Scanner Professionale AI", layout="centered")

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

if not st.session_state['autenticato']:
    st.title("📲 Portale Documenti AI")
    st.info("Inserisci le tue credenziali a sinistra per iniziare.")
    st.stop()

# --- APP LIVE ---
st.title("📑 Scanner Fatture Professionale")

file = st.file_uploader("Carica o scatta una foto", type=['jpg', 'jpeg', 'png'])

if file:
    img = Image.open(file)
    st.image(img, caption="Documento caricato", use_container_width=True)
    
    if st.button("🔍 ANALIZZA DOCUMENTO"):
        try:
            with st.spinner("L'intelligenza artificiale sta leggendo i dati..."):
                # CAMBIO MODELLO: Usiamo 'gemini-1.5-pro' che è il più stabile
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                prompt = "Analizza l'immagine e scrivi: Fornitore, Data e Totale."
                response = model.generate_content([prompt, img])
                
                st.success("✅ Analisi completata!")
                st.subheader("Dati Estratti:")
                st.write(response.text)
                st.balloons()
        except Exception as e:
            # Se fallisce anche il Pro, proviamo senza prefissi
            try:
                model = genai.GenerativeModel('gemini-pro-vision')
                response = model.generate_content(["Estrai fornitore, data e totale", img])
                st.write(response.text)
            except:
                st.error(f"Errore tecnico: {e}")
                st.info("Controlla che la tua API KEY su Google AI Studio sia attiva.")
