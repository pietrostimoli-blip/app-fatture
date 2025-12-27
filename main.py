import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURAZIONE FORZATA V1
try:
    # Usiamo la nuova chiave dai Secrets
    API_KEY = st.secrets["API_KEY"]
    # Forziamo il client a usare la versione 1 stabile, non la beta
    genai.configure(api_key=API_KEY, transport='rest')
except Exception:
    st.error("Errore: API_KEY non configurata correttamente nei Secrets!")
    st.stop()

# 2. ACCESSI
UTENTI = {"admin": "tuapassword", "negozio1": "pass123"}

st.set_page_config(page_title="Scanner Professionale AI", layout="centered")

if 'autenticato' not in st.session_state:
    st.session_state['autenticato'] = False

# SIDEBAR LOGIN
st.sidebar.title("🔐 Accesso")
user = st.sidebar.text_input("Utente")
passw = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Accedi"):
    if user in UTENTI and UTENTI[user] == passw:
        st.session_state['autenticato'] = True
        st.rerun()

if not st.session_state['autenticato']:
    st.info("Inserisci le credenziali a sinistra.")
    st.stop()

# APP LIVE
st.title("📑 Scanner Multi-Formato")
file = st.file_uploader("Carica Fattura", type=['pdf', 'jpg', 'jpeg', 'png'])

if file:
    if st.button("🔍 ANALIZZA ORA"):
        try:
            with st.spinner("Analisi in corso..."):
                # Specifichiamo il modello senza prefissi per massima compatibilità
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                if file.type == "application/pdf":
                    documento = {"mime_type": "application/pdf", "data": file.read()}
                    response = model.generate_content(["Estrai: Fornitore, Data e Totale.", documento])
                else:
                    img = Image.open(file)
                    response = model.generate_content(["Estrai: Fornitore, Data e Totale.", img])
                
                st.subheader("Risultato:")
                st.write(response.text)
                st.balloons()
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
