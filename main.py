import streamlit as st
import requests
import base64

# CONFIGURAZIONE
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    st.error("Manca API_KEY nei Secrets!")
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
    st.info("Esegui il login a sinistra.")
    st.stop()

# APP
st.title("📑 Scanner Intelligente (Auto-Fix)")
file = st.file_uploader("Carica Documento", type=['pdf', 'jpg', 'jpeg', 'png'])

if file and st.button("🔍 ANALIZZA ORA"):
    try:
        with st.spinner("Ricerca modello compatibile con la tua chiave..."):
            # 1. CHIEDIAMO A GOOGLE QUALI MODELLI PUOI USARE
            list_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
            list_res = requests.get(list_url).json()
            
            modelli_validi = []
            if 'models' in list_res:
                for m in list_res['models']:
                    # Cerchiamo modelli che supportano la generazione di contenuti
                    if 'generateContent' in m.get('supportedGenerationMethods', []):
                        modelli_validi.append(m['name'])
            
            if not modelli_validi:
                st.error("La tua chiave API non ha modelli abilitati. Controlla Google AI Studio.")
                st.stop()

            # 2. PROVIAMO IL PRIMO MODELLO DISPONIBILE
            target_model = modelli_validi[0] 
            st.info(f"Sto usando il modello: {target_model}")

            file_data = base64.b64encode(file.read()).decode("utf-8")
            mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
            
            url = f"https://generativelanguage.googleapis.com/v1/{target_model}:generateContent?key={API_KEY}"
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
                st.balloons()
            else:
                st.error(f"Errore specifico: {result['error']['message']}")
                
    except Exception as e:
        st.error(f"Errore di sistema: {e}")
