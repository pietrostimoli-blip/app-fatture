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
st.title("📑 Scanner Fatture & PDF")

# QUESTA RIGA È QUELLA CHE ABILITA IL PDF
file = st.file_uploader("Carica Fattura", type=['pdf', 'jpg', 'jpeg', 'png'])

if file:
    st.success(f"File caricato: {file.name}")
    
    if st.button("🔍 ANALIZZA DOCUMENTO"):
        try:
            with st.spinner("L'intelligenza artificiale sta leggendo il file..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                if file.type == "application/pdf":
                    # Lettura specifica per PDF
                    file_data = file.read()
                    response = model.generate_content([
                        "Estrai Fornitore, Data e Totale da questo PDF.",
                        {"mime_type": "application/pdf", "data": file_data}
                    ])
                else:
                    # Lettura per Immagini
                    img = Image.open(file)
                    response = model.generate_content(["Estrai Fornitore, Data e Totale.", img])
                
                st.subheader("Dati Estratti:")
                st.write(response.text)
                st.balloons()
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
