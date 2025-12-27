import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configurazione Pagina
st.set_page_config(page_title="DEBUG AI Dashboard", layout="wide")

# 2. Configurazione Link (Assicurati che ci siano le virgolette e l'URL intero)
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_EXEC"

# 3. Utenti
UTENTI = {"admin": "12345", "negozio1": "pass1"}

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u in UTENTI and UTENTI[u] == p:
            st.session_state['auth'] = True
            st.session_state['user'] = u
            st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title(f"📊 Utente Attivo: {st.session_state['user']}")

up = st.file_uploader("Carica un file per testare", type=['pdf', 'jpg', 'png', 'xml'])

if up and st.button("🔍 ANALIZZA ORA"):
    st.warning("🚀 Fase 1: Tasto premuto correttamente!") # Segnale 1
    
    try:
        # Controllo Secrets
        if "API_KEY" not in st.secrets:
            st.error("❌ ERRORE: La API_KEY non è configurata nei Secrets di Streamlit!")
            st.stop()
        
        st.info("🤖 Fase 2: API_KEY trovata. Invio all'AI...") # Segnale 2
        
        API_KEY = st.secrets["API_KEY"]
        file_bytes = up.read()
        
        # Preparazione prompt
        prompt = "Estrai Soggetto, Data, Totale, Imponibile, IVA, Scadenza, Articoli. Rispondi SOLO con i valori separati da virgola."
        
        if up.name.lower().endswith('.xml'):
            testo_xml = file_bytes.decode('utf-8', errors='ignore')
            payload_ai = {"contents": [{"parts": [{"text": f"{prompt}\n\n{testo_xml}"}]}]}
        else:
            b64 = base64.b64encode(file_bytes).decode()
            payload_ai = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": up.type, "data": b64}}]}]}
        
        # Chiamata AI
        url_ai = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        res_ai = requests.post(url_ai, json=payload_ai).json()
        
        if 'candidates' in res_ai:
            st.success("✨ Fase 3: L'AI ha risposto!") # Segnale 3
            testo = res_ai['candidates'][0]['content']['parts'][0]['text']
            dati = [i.strip() for i in testo.split(',')]
            
            st.write("Dati estratti:", dati)
            
            # Invio a Google
            st.info(f"📤 Fase 4: Invio al foglio di {st.session_state['user']}...") # Segnale 4
            
            payload_google = {
                "utente": st.session_state['user'],
                "tipo": "ACQUISTO",
                "soggetto": dati[0],
                "data_doc": dati[1],
                "totale": dati[2],
                "imponibile": dati[3],
                "iva": dati[4],
                "note": dati[6] if len(dati) > 6 else "N/D"
            }
            
            r_google = requests.post(WEBHOOK_URL, json=payload_google)
            
            if r_google.status_code == 200:
                st.success("✅ OPERAZIONE COMPLETATA! Controlla il foglio Google.")
                st.balloons()
            else:
                st.error(f"❌ Errore Google (Fase 4): {r_google.status_code}")
        else:
            st.error(f"❌ Errore AI (Fase 3): {res_ai}")
            
    except Exception as e:
        st.error(f"❌ ERRORE CRITICO: {e}")
