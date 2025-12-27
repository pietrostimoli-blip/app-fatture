Capisco perfettamente la frustrazione. L'errore persiste perché la libreria google-generativeai installata sui server di Streamlit sta forzando l'uso di un indirizzo (endpoint) che Google ha rimosso o spostato per il modello Flash.

Proviamo la mossa finale: cambiamo il modello in gemini-1.5-pro (come suggerito dal messaggio di errore stesso) e semplifichiamo al massimo la chiamata. Il modello Pro è più "robusto" e spesso viaggia su canali diversi che non danno questo errore 404.

🛠️ Codice Definitivo "Versione Pro"
Copia e sostituisci tutto su GitHub. Ho aggiornato il modello e pulito il codice per evitare conflitti.

Python

import streamlit as st
import google.generativeai as genai
from PIL import Image

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
st.title("📑 Scanner Fatture & PDF (Versione Pro)")
file = st.file_uploader("Carica Fattura", type=['pdf', 'jpg', 'jpeg', 'png'])

if file:
    if st.button("🔍 ANALIZZA DOCUMENTO"):
        try:
            with st.spinner("Analisi in corso con Gemini Pro..."):
                # PASSIAMO AL MODELLO PRO PER BYPASSARE L'ERRORE 404
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                if file.type == "application/pdf":
                    file_data = file.read()
                    response = model.generate_content([
                        "Estrai Fornitore, Data e Totale da questo documento PDF.",
                        {"mime_type": "application/pdf", "data": file_data}
                    ])
                else:
                    img = Image.open(file)
                    response = model.generate_content(["Estrai Fornitore, Data e Totale da questa immagine.", img])
                
                st.subheader("Risultato:")
                if response.text:
                    st.write(response.text)
                    st.balloons()
                else:
                    st.warning("L'AI ha analizzato il file ma non ha prodotto testo.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
            st.info("Se l'errore 404 persiste anche col modello Pro, è necessario creare un
