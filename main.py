import streamlit as st
import requests
import base64

st.set_page_config(page_title="Gemini Multi-Database", layout="wide")

# INCOLLA QUI L'ULTIMO URL COPIATO
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxvo4G1fUpgL8rMdEwobt4OTVQIeCzioU6B5JPjacwBwPJXMjIyYmnM6Zyhub0pfik/exec"

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
    try:
        with st.spinner("1. Chiamata a Gemini in corso..."):
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
                st.info("✅ Gemini ha risposto! Invio i dati a Google Sheets...")
                testo = res_ai['candidates'][0]['content']['parts'][0]['text']
                d = [i.strip() for i in testo.split(',')]
                while len(d) < 7: d.append("N/D")
                
                payload_google = {
                    "utente": st.session_state['user'], "tipo": "ACQUISTO",
                    "soggetto": d[0], "data_doc": d[1], "totale": d[2],
                    "imponibile": d[3], "iva": d[4], "note": d[6]
                }
                
                # INVIO A GOOGLE CON TIMEOUT
                r = requests.post(WEBHOOK_URL, json=payload_google, timeout=15)
                
                if r.status_code == 200:
                    st.success(f"🎉 Successo! Dati scritti nel tab '{st.session_state['user']}'")
                    st.balloons()
                else:
                    st.error(f"Errore Google Sheets: {r.status_code}")
            else:
                st.error("Errore Gemini: Controlla la tua API KEY nei Secrets.")
                
    except requests.exceptions.Timeout:
        st.error("⏳ Timeout: Google Sheets non risponde. Controlla la distribuzione dello script (deve essere 'Chiunque').")
    except Exception as e:
        st.error(f"Errore generico: {e}")
