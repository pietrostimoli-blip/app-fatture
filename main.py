import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# 1. CONFIGURAZIONE
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Errore: API_KEY non trovata nei Secrets!")
    st.stop()

# 2. ACCESSI
UTENTI = {"admin": "tuapassword", "negozio1": "pass123"}

st.set_page_config(page_title="Scanner Professionale AI", layout="centered")

if 'autenticato' not in st.session_state:
    st.session_state['autenticato'] = False

# SIDEBAR LOGIN
st.sidebar.title("🔐 Accesso")
user = st.sidebar.text_input("Utente")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Accedi"):
    if user in UTENTI and UTENTI[user] == password:
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
            with st.spinner("Analisi in corso sulla rete stabile Google..."):
                # Usiamo il modello Flash con la configurazione più compatibile possibile
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                )
                
                if file.type == "application/pdf":
                    documento = {"mime_type": "application/pdf", "data": file.read()}
                    # Forziamo la chiamata
                    response = model.generate_content(
                        ["Estrai Fornitore, Data e Totale da questo PDF.", documento]
                    )
                else:
                    img = Image.open(file)
                    response = model.generate_content(
                        ["Estrai Fornitore, Data e Totale.", img]
                    )
                
                st.subheader("Risultato:")
                if response.text:
                    st.write(response.text)
                    st.balloons()
                else:
                    st.warning("L'AI non ha prodotto testo. Verifica il contenuto del file.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
            st.info("Se l'errore 404 persiste, Google sta bloccando l'accesso v1beta dalla tua area. Proviamo a cambiare il nome del modello in 'gemini-1.5-pro' nel codice.")
