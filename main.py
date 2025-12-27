import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAZIONE SICURA ---
try:
    API_KEY = st.secrets["API_KEY"]
    SHEET_ID = st.secrets["SHEET_ID"]
except:
    st.error("Errore: Configura API_KEY e SHEET_ID nei Secrets di Streamlit!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- LISTA ACCESSI CLIENTI (Aggiungi qui chi vuoi) ---
UTENTI_AUTORIZZATI = {
    "admin": "tuapassword",
    "negozio1": "pass123"
}

st.set_page_config(page_title="Scanner Fatture Pro", layout="centered")

# --- SIDEBAR PULITA (Solo Login) ---
st.sidebar.title("🔐 Accesso Clienti")
utente = st.sidebar.text_input("Nome Utente")
password = st.sidebar.text_input("Password", type="password")

# --- CONTROLLO ACCESSO ---
if utente in UTENTI_AUTORIZZATI and UTENTI_AUTORIZZATI[utente] == password:
    
    st.title(f"📑 Benvenuto, {utente.capitalize()}")
    st.info("Carica una fattura per estrarre i dati e salvarli nel database.")

    # --- SCANNER ---
    file = st.file_uploader("Scatta o carica foto", type=['jpg', 'jpeg', 'png'])

    if file:
        img = Image.open(file)
        st.image(img, width=400)

        if st.button("🔍 ANALIZZA E INVIA"):
            with st.spinner("Analisi in corso..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Estrai Fornitore, Data e Totale. Rispondi: Fornitore | Data | Totale"
                response = model.generate_content([prompt, img])
                
                st.success("✅ Dati inviati con successo!")
                st.markdown(f"**Risultato:** {response.text}")
                # Il sistema userà 'utente' per segnare chi ha mandato il file nel foglio Google
else:
    st.title("📲 Portale Acquisizione Fatture")
    st.warning("Inserisci le credenziali nella barra laterale per accedere.")
    st.stop()
