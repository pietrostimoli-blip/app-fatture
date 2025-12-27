import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Deve essere la PRIMISSIMA riga di codice Streamlit
st.set_page_config(page_title="Gestionale AI Universale", layout="wide")

# 2. CONFIGURAZIONE WEBHOOK (Incolla il tuo link che finisce con /exec)
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_APPS_SCRIPT"

# --- STILE GRAFICO DASHBOARD ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .main-card { background: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    .stButton>button { background-color: #238636; color: white; width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Accesso Gestionale</h2>", unsafe_allow_html=True)
        u = st.text_input("User", key="user_login")
        p = st.text_input("Password", type="password", key="pass_login")
        if st.button("ACCEDI"):
            if u == "admin" and p == "tuapassword":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Credenziali errate")
    st.stop()

# --- INTERFACCIA PRINCIPALE ---
st.title("📊 Gestionale AI: Foto, PDF e XML")
st.write("Archiviazione automatica su Google Sheets")

with st.sidebar:
    st.header("📤 Caricamento")
    file = st.file_uploader("Documento (PDF, JPG, PNG, XML)", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'])
    st.markdown("---")
    if st.button("🚪 Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    if st.button("🚀 ANALIZZA E ARCHIVIA NEL CLOUD"):
        try:
            with st.spinner("Elaborazione e salvataggio in corso..."):
                API_KEY = st.secrets["API_KEY"]
                file_bytes = file.read()
                
                # LOGICA PER FATTURA ELETTRONICA (XML)
                if file.name.lower().endswith('.xml'):
                    content = file_bytes.decode("utf-8")
                    prompt_text = f"Analizza questo XML. Estrai: Fornitore, Data, Totale, Imponibile, IVA, Note. Rispondi SOLO con i valori separati da virgola:\n\n{content}"
                    payload_ai = {
                        "contents": [{"parts": [{"text": prompt_text}]}]
                    }
                # LOGICA PER IMMAGINI E PDF
                else:
                    file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                    mime_type = file.type
                    payload_ai = {
                        "contents": [{
                            "parts": [
                                {"text": "Analizza il documento e restituisci SOLO Fornitore, Data, Totale, Imponibile, IVA, Note separati da virgola. Se manca scrivi 0."},
                                {"inline_data": {"mime_type": mime_type, "data": file_b64}}
                            ]
                        }]
                    }
                
                # 1. Chiamata a Google Gemini
                url_ai = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                res_ai = requests.post(url_ai, json=payload_ai).json()
                
                if 'candidates' in res_ai:
                    testo_estratto = res_ai['candidates'][0]['content']['parts'][0]['text']
                    d = [item.strip() for item in testo_estratto.split(',')]
                    while len(d) < 6: d.append("0")
                    
                    # 2. Invio dati a Google Sheets
                    dati_per_sheets = {
                        "fornitore": d[0], "data_fattura": d[1], "totale": d[2],
                        "imponibile": d[3], "iva": d[4], "note": d[5]
                    }
                    
                    response_sheets = requests.post(WEBHOOK_URL, json=dati_per_sheets)
                    
                    if response_sheets.status_code == 200:
                        st.success("✅ Salvataggio completato su Google Sheets!")
                        st.balloons()
                        st.markdown(f"""
                        <div style="background:#1c2128; padding:15px; border-radius:10px; border:1px solid #30363d;">
                            <b>Fornitore:</b> {d[0]}<br>
                            <b>Totale:</b> {d[2]} €<br>
                            <b>Data:</b> {d[1]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Errore scrittura Sheets (Codice: {response_sheets.status_code})")
                else:
                    st.error("L'AI non ha risposto correttamente. Verifica il file.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {e}")

st.markdown("---")
st.markdown(f"🔗 [Apri il tuo Database Google Sheets](https://docs.google.com/spreadsheets/d/13YmESjh6YHVENUwAX1VQPdKPOOULHwv1HU_Y7jOBGn4)")
