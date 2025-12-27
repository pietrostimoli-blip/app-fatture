import streamlit as st
import requests
import base64
import pandas as pd

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scanner Fatture", page_icon="🧾", layout="centered")

if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    st.error("Manca API_KEY nei Secrets!")
    st.stop()

# Inizializza lo storico dei dati nella memoria della sessione
if 'storico' not in st.session_state:
    st.session_state['storico'] = []

# --- STILE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .login-container { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<h2 style='text-align: center;'>🔐 Accesso Scanner</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Accedi"):
                if u == "admin" and p == "tuapassword": # Cambia qui se vuoi
                    st.session_state['auth'] = True
                    st.rerun()
                else: st.error("Dati errati")
    st.stop()

# --- APP PRINCIPALE ---
st.title("🧾 Scanner Rapido Fatture")
st.write("Estrae automaticamente Fornitore, Data e Totale.")

file = st.file_uploader("Carica file (PDF o Immagine)", type=['pdf', 'jpg', 'png'])

if file and st.button("🔍 ANALIZZA E MEMORIZZA"):
    try:
        with st.spinner("Analisi in corso..."):
            # Auto-scoperta modello
            list_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
            list_res = requests.get(list_url).json()
            target_model = next((m['name'] for m in list_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])), "models/gemini-1.5-flash")

            file_data = base64.b64encode(file.read()).decode("utf-8")
            mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
            
            # Prompt focalizzato solo sui 3 dati richiesti
            url = f"https://generativelanguage.googleapis.com/v1/{target_model}:generateContent?key={API_KEY}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Estrai solo questi dati in formato JSON: {'fornitore': '...', 'data': '...', 'totale': '...'}. Non scrivere altro testo."},
                        {"inline_data": {"mime_type": mime_type, "data": file_data}}
                    ]
                }]
            }
            
            response = requests.post(url, json=payload)
            res_json = response.json()
            
            if response.status_code == 200:
                output = res_json['candidates'][0]['content']['parts'][0]['text']
                # Pulizia testo per ottenere solo i dati
                st.subheader("✅ Ultimo Risultato")
                st.code(output)
                
                # Aggiunta allo storico della sessione
                st.session_state['storico'].append(output)
                st.balloons()
            else:
                st.error("Errore durante l'analisi.")

    except Exception as e:
        st.error(f"Errore: {e}")

# --- SEZIONE STORICO ---
if st.session_state['storico']:
    st.markdown("---")
    st.subheader("📚 Storico Analisi Recenti")
    for item in st.session_state['storico']:
        st.text(item)
    
    if st.button("Cancella Storico"):
        st.session_state['storico'] = []
        st.rerun()
