import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Business Dashboard", layout="wide")

# 2. CONFIGURAZIONE LINK GOOGLE (Incolla il tuo URL /exec tra le virgolette)
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_APPS_SCRIPT"

# 3. LISTA UTENTI AUTORIZZATI
UTENTI_AUTORIZZATI = {
    "admin": "12345",
    "ufficio": "2025",
    "negozio1": "scelta1"
}

# --- STILE GRAFICO ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .login-card { 
        background: #161b22; padding: 30px; border-radius: 15px; 
        border: 1px solid #30363d; margin-top: 50px;
    }
    .stButton>button { background-color: #238636; color: white; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DI LOGIN ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🔐 Accesso Gestionale</h2>", unsafe_allow_html=True)
        user_in = st.text_input("Username")
        pass_in = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if user_in in UTENTI_AUTORIZZATI and UTENTI_AUTORIZZATI[user_in] == pass_in:
                st.session_state['auth'] = True
                st.session_state['user_attivo'] = user_in
                st.rerun()
            else:
                st.error("Credenziali errate")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACCIA DOPO IL LOGIN ---
st.title(f"📊 Dashboard: {st.session_state['user_attivo']}")

tab1, tab2 = st.tabs(["📥 ACQUISTI (Fornitori)", "📤 VENDITE (Clienti)"])

with tab1:
    st.subheader("Carica Fattura Acquisto")
    file_acq = st.file_uploader("Scegli file (PDF, JPG, XML)", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'])
    if file_acq and st.button("🚀 ANALIZZA E ARCHIVIA"):
        try:
            with st.spinner("L'AI sta leggendo..."):
                API_KEY = st.secrets["API_KEY"]
                file_bytes = file_acq.read()
                
                prompt = "Estrai Soggetto, DataDocumento, Totale, Imponibile, IVA, Scadenza, Articoli. Rispondi SOLO con i valori separati da virgola."
                
                if file_acq.name.lower().endswith('.xml'):
                    payload = {"contents": [{"parts": [{"text": f"{prompt}\n{file_bytes.decode('utf-8')}"}]}]}
                else:
                    file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": file_acq.type, "data": file_b64}}]}]}
                
                res = requests.post(f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}", json=payload).json()
                d = [item.strip() for item in res['candidates'][0]['content']['parts'][0]['text'].split(',')]
                while len(d) < 7: d.append("0")

                payload_sheets = {
                    "tipo": "ACQUISTO",
                    "soggetto": d[0],
                    "data_doc": d[1],
                    "totale": d[2],
                    "imponibile": d[3],
                    "iva": d[4],
                    "scadenza": d[5],
                    "note": f"Articoli: {d[6]} | Op: {st.session_state['user_attivo']}"
                }
                
                resp = requests.post(WEBHOOK_URL, json=payload_sheets)
                if resp.status_code == 200:
                    st.success(f"Archiviato: {d[0]} ({d[2]}€)")
                    st.balloons()
        except Exception as e:
            st.error(f"Errore: {e}")

with tab2:
    st.subheader("Registra Fattura Vendita")
    with st.form("form_v"):
        c = st.text_input("Nome Cliente")
        t = st.number_input("Totale Fattura (€)", min_value=0.0)
        s = st.date_input("Scadenza Pagamento")
        n = st.text_area("Articoli / Note")
        if st.form_submit_button("💾 SALVA VENDITA"):
            imp = t / 1.22
            p_v = {
                "tipo": "VENDITA", "soggetto": c, "data_doc": str(datetime.now().date()),
                "totale": t, "imponibile": round(imp, 2), "iva": round(t-imp, 2),
                "scadenza": str(s), "note": n
            }
            requests.post(WEBHOOK_URL, json=p_v)
            st.success("Vendita registrata nel Cloud!")

if st.sidebar.button("🚪 Logout"):
    st.session_state['auth'] = False
    st.rerun()
