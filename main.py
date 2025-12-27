import streamlit as st
import requests
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Cloud Scanner AI", page_icon="📑", layout="centered")

# --- STILE CSS PER INTERFACCIA CARINA ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .login-box {
        padding: 30px;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAZIONE API ---
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    st.error("Manca API_KEY nei Secrets!")
    st.stop()

# --- GESTIONE LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #1e3d59;'>🔐 Benvenuto</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Inserisci le tue credenziali per accedere allo scanner</p>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="Es: admin")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            if st.button("Accedi al Sistema"):
                UTENTI = {"admin": "tuapassword", "negozio1": "pass123"}
                if u in UTENTI and UTENTI[u] == p:
                    st.session_state['auth'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Credenziali errate")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- APP PRINCIPALE (DOPO LOGIN) ---
st.markdown(f"<p style='text-align: right;'>👤 Utente: <b>{st.session_state['user']}</b></p>", unsafe_allow_html=True)
st.title("📑 Cloud Scanner AI")
st.write("Carica una fattura o un PDF per estrarre tutti i dati automaticamente.")

file = st.file_uploader("Trascina qui il file", type=['pdf', 'jpg', 'jpeg', 'png'])

if file:
    st.info(f"File pronto per l'analisi: {file.name}")
    
    if st.button("🔍 AVVIA ANALISI DETTAGLIATA"):
        try:
            with st.spinner("L'AI sta analizzando ogni dettaglio..."):
                # 1. Ricerca modello (Auto-fix che abbiamo testato prima)
                list_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
                list_res = requests.get(list_url).json()
                target_model = next((m['name'] for m in list_res.get('models', []) 
                                   if 'generateContent' in m.get('supportedGenerationMethods', [])), None)
                
                if not target_model:
                    st.error("Nessun modello disponibile.")
                    st.stop()

                # 2. Preparazione dati
                file_data = base64.b64encode(file.read()).decode("utf-8")
                mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                # 3. Prompt Potenziato
                url = f"https://generativelanguage.googleapis.com/v1/{target_model}:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": """Analizza questo documento in modo professionale. Estrai:
                             - Dati del Fornitore (Nome, P.IVA, Indirizzo)
                             - Dati del Cliente
                             - Data e Numero Fattura
                             - Elenco puntato di tutti i prodotti/servizi con prezzi
                             - Riepilogo IVA e Imponibile
                             - Totale Documento
                             - IBAN o Metodo di pagamento se presente.
                             Formatta tutto in modo leggibile."""},
                            {"inline_data": {"mime_type": mime_type, "data": file_data}}
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload)
                result = response.json()
                
                if response.status_code == 200:
                    testo = result['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("---")
                    st.subheader("📊 Risultato dell'Estrazione")
                    st.markdown(testo)
                    st.balloons()
                else:
                    st.error(f"Errore Google: {result['error']['message']}")
        except Exception as e:
            st.error(f"Errore: {e}")

# --- LOGOUT ---
if st.sidebar.button("Esci"):
    st.session_state['auth'] = False
    st.rerun()
