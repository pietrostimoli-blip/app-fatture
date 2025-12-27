import streamlit as st
import requests
import base64

# CONFIGURAZIONE
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    st.error("Inserisci API_KEY nei Secrets!")
    st.stop()

# LOGIN
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
    st.info("Esegui il login.")
    st.stop()

# APP
st.title("📑 Scanner Definitivo (Versione V1)")
file = st.file_uploader("Carica Documento", type=['pdf', 'jpg', 'jpeg', 'png'])

if file and st.button("🔍 ANALIZZA ORA"):
    try:
        with st.spinner("Comunicazione diretta con Google in corso..."):
            # Prepariamo il file
            file_data = base64.b64encode(file.read()).decode("utf-8")
            mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
            
            # URL Forzato alla versione V1 (NON v1beta)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Estrai Fornitore, Data e Totale da questo documento."},
                        {"inline_data": {"mime_type": mime_type, "data": file_data}}
                    ]
                }]
            }
            
            response = requests.post(url, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                testo = result['candidates'][0]['content']['parts'][0]['text']
                st.success("Analisi Completata!")
                st.write(testo)
            else:
                st.error(f"Errore Google: {result['error']['message']}")
                
    except Exception as e:
        st.error(f"Errore: {e}")
