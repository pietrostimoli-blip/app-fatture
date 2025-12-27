import streamlit as st
import requests
import base64

st.set_page_config(page_title="Gemini Business AI", layout="wide")

# METTI QUI IL NUOVO URL CHE HAI APPENA COPIATO
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzxfFiKXTD5gkY_bKeMTYDdGnV_WYY1iA9ZmBaNLO1XZQLpgrXJPFW2vMgXu41jOplG/exec"

UTENTI = {"admin": "12345", "negozio1": "pass1"}

if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("ACCEDI"):
        if u in UTENTI and UTENTI[u] == p:
            st.session_state['auth'] = True
            st.session_state['user'] = u
            st.rerun()
    st.stop()

st.title(f"📊 Dashboard: {st.session_state['user']}")

up = st.file_uploader("Carica file", type=['pdf', 'jpg', 'png', 'xml'])

if up and st.button("🔍 ANALIZZA E ARCHIVIA"):
    with st.spinner("Gemini sta lavorando..."):
        try:
            # 1. Chiamata a Gemini
            API_KEY = st.secrets["API_KEY"]
            file_bytes = up.read()
            prompt = "Estrai: Soggetto, Data, Totale, Imponibile, IVA, Scadenza, Articoli. Rispondi solo con i valori separati da virgola."
            
            if up.name.lower().endswith('.xml'):
                payload_ai = {"contents": [{"parts": [{"text": f"{prompt}\n\n{file_bytes.decode('utf-8', errors='ignore')}"}]}]}
            else:
                payload_ai = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": up.type, "data": base64.b64encode(file_bytes).decode()}}]}]}
            
            url_ai = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            res_ai = requests.post(url_ai, json=payload_ai).json()
            
            if 'candidates' in res_ai:
                testo = res_ai['candidates'][0]['content']['parts'][0]['text']
                d = [i.strip() for i in testo.split(',')]
                while len(d) < 7: d.append("N/D")
                
                # 2. Invio a Google con TIMEOUT per non bloccarsi
                payload_google = {
                    "utente": st.session_state['user'], "tipo": "ACQUISTO",
                    "soggetto": d[0], "data_doc": d[1], "totale": d[2],
                    "imponibile": d[3], "iva": d[4], "note": d[6]
                }
                
                st.info("AI ha risposto. Invio i dati al foglio...")
                r = requests.post(WEBHOOK_URL, json=payload_google, timeout=10) # 10 secondi max
                
                if r.status_code == 200:
                    st.success(f"Archiviato in {st.session_state['user']}!")
                    st.balloons()
                else:
                    st.error(f"Il foglio Google ha risposto con errore: {r.status_code}")
            else:
                st.error("Gemini non ha riconosciuto il file. Controlla la API KEY.")
                
        except requests.exceptions.Timeout:
            st.error("⏳ Google Sheets ci sta mettendo troppo a rispondere. Controlla se lo script è attivo.")
        except Exception as e:
            st.error(f"Errore: {e}")
