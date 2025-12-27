import streamlit as st
import google.generativeai as genai
from PIL import Image

# FORZIAMO IL MODELLO PRO E LA VERSIONE STABILE
MODEL_NAME = "gemini-1.5-pro" 

try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Chiave API non trovata!")
    st.stop()

# LOGIN SEMPLIFICATO
UTENTI = {"admin": "tuapassword", "negozio1": "pass123"}
if 'auth' not in st.session_state: st.session_state['auth'] = False

st.sidebar.title("🔐 Accesso")
u = st.sidebar.text_input("User")
p = st.sidebar.text_input("Pass", type="password")
if st.sidebar.button("Entra"):
    if u in UTENTI and UTENTI[u] == p:
        st.session_state['auth'] = True
        st.rerun()

if not st.session_state['auth']:
    st.info("Esegui il login a sinistra.")
    st.stop()

# APP PRINCIPALE
st.title("📑 Scanner Definitivo (Versione Pro)")
file = st.file_uploader("Carica Documento", type=['pdf', 'jpg', 'jpeg', 'png'])

if file and st.button("🔍 ANALIZZA ORA"):
    try:
        with st.spinner("Analisi in corso..."):
            model = genai.GenerativeModel(MODEL_NAME)
            
            if file.type == "application/pdf":
                content = [{"mime_type": "application/pdf", "data": file.read()}]
                res = model.generate_content(["Cosa c'è in questo PDF? Estrai Fornitore, Data e Totale.", content[0]])
            else:
                img = Image.open(file)
                res = model.generate_content(["Analizza immagine: Fornitore, Data e Totale.", img])
            
            st.success("Dati Estratti:")
            st.write(res.text)
    except Exception as e:
        st.error(f"Errore: {e}")
