import streamlit as st
import requests
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Scanner Fatture Pro", page_icon="🧾", layout="wide")

# --- STILE CSS MODERN DASHBOARD ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .login-box {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .data-label { color: #555; font-weight: bold; font-size: 0.9em; }
    .data-value { color: #1e3d59; font-size: 1.1em; margin-bottom: 10px; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #1e3d59;
        color: white;
        font-weight: bold;
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
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 Cloud Scanner</h2>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.session_state['user'] = u
            st.rerun()
        else: st.error("Credenziali errate")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- APP PRINCIPALE ---
st.markdown(f"<p style='text-align: right;'>👤 <b>{st.session_state['user']}</b></p>", unsafe_allow_html=True)
st.title("📑 Analisi Completa Documento")

col_input, col_output = st.columns([1, 1.2])

with col_input:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📤 Carica Documento")
    file = st.file_uploader("PDF o Immagine", type=['pdf', 'jpg', 'jpeg', 'png'])
    if file:
        st.success(f"File pronto: {file.name}")
        btn_analizza = st.button("🔍 AVVIA ESTRAZIONE COMPLETA")
    st.markdown('</div>', unsafe_allow_html=True)

with col_output:
    st.subheader("📋 Dati Documento")
    if file and btn_analizza:
        try:
            with st.spinner("Estrazione in corso di tutti i dettagli..."):
                # Bypass errore 404
                list_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
                list_res = requests.get(list_url).json()
                target_model = next((m['name'] for m in list_res.get('models', []) 
                                   if 'generateContent' in m.get('supportedGenerationMethods', [])), "models/gemini-1.5-flash")

                file_data = base64.b64encode(file.read()).decode("utf-8")
                mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                url = f"https://generativelanguage.googleapis.com/v1/{target_model}:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": """Analizza questa fattura o scontrino ed estrai OGNI dettaglio:
                             1. Intestazione (Fornitore, P.IVA, Indirizzo, Telefono)
                             2. Numero Documento e Data
                             3. Tabella Prodotti (Descrizione, Quantità, Prezzo Unitario, Totale riga)
                             4. Totali (Imponibile, IVA per aliquota, Totale complessivo)
                             5. Metodo di pagamento e IBAN se presenti.
                             Presenta i dati in modo molto ordinato con titoli chiari."""},
                            {"inline_data": {"mime_type": mime_type, "data": file_data}}
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload)
                result = response.json()
                
                if response.status_code == 200:
                    testo_estratto = result['candidates'][0]['content']['parts'][0]['text']
                    st.markdown('<div class="main-card">', unsafe_allow_html=True)
                    st.markdown(testo_estratto)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Bottone per non perdere i dati
                    st.download_button("💾 Salva Analisi (Testo)", testo_estratto, file_name=f"analisi_{file.name}.txt")
                    st.balloons()
                else:
                    st.error(f"Errore: {result['error']['message']}")
        except Exception as e:
            st.error(f"Errore di sistema: {e}")
    else:
        st.info("In attesa di scansione...")

# Sidebar
with st.sidebar:
    if st.button("Esci"):
        st.session_state['auth'] = False
        st.rerun()
