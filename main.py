import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Business Dashboard", layout="wide")

# 2. CONFIGURAZIONE LINK GOOGLE (Sostituisci col tuo URL /exec)
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
    .login-card { background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; margin-top: 50px; }
    .stButton>button { background-color: #238636; color: white; font-weight: bold; width: 100%; height: 3em; }
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

# --- FUNZIONE ANALISI AI (UNIFICATA) ---
def analizza_documento(file, tipo_doc):
    try:
        API_KEY = st.secrets["API_KEY"]
        file_bytes = file.read()
        prompt = f"Analizza questa fattura di {tipo_doc}. Estrai: 1.Soggetto, 2.DataDoc, 3.Totale, 4.Imponibile, 5.IVA, 6.Scadenza, 7.Articoli. Rispondi SOLO con i valori separati da virgola."
        
        if file.name.lower().endswith('.xml'):
            xml_text = file_bytes.decode('utf-8')
            payload = {"contents": [{"parts": [{"text": f"{prompt}\n\n{xml_text}"}]}]}
        else:
            file_b64 = base64.b64encode(file_bytes).decode("utf-8")
            payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": file.type, "data": file_b64}}]}]}
        
        res = requests.post(f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}", json=payload).json()
        
        if 'candidates' in res:
            testo = res['candidates'][0]['content']['parts'][0]['text']
            dati = [item.strip() for item in testo.split(',')]
            while len(dati) < 7: dati.append("N/D")
            return dati
        return None
    except Exception as e:
        st.error(f"Errore AI: {e}")
        return None

# --- INTERFACCIA PRINCIPALE ---
st.title(f"📊 Dashboard: {st.session_state['user_attivo']}")
tab1, tab2 = st.tabs(["📥 ACQUISTI", "📤 VENDITE"])

# --- TAB ACQUISTI ---
with tab1:
    st.subheader("Importa Fattura Acquisto")
    file_acq = st.file_uploader("Carica PDF, Foto o XML", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'], key="up_acq")
    if file_acq and st.button("🔍 ANALIZZA ACQUISTO"):
        d = analizza_documento(file_acq, "ACQUISTO")
        if d:
            payload = {"tipo": "ACQUISTO", "soggetto": d[0], "data_doc": d[1], "totale": d[2], "imponibile": d[3], "iva": d[4], "scadenza": d[5], "note": d[6]}
            if requests.post(WEBHOOK_URL, json=payload).status_code == 200:
                st.success(f"Acquisto da {d[0]} salvato!")
                st.balloons()

# --- TAB VENDITE ---
with tab2:
    st.subheader("Gestione Vendite")
    scelta = st.radio("Metodo di inserimento:", ["Carica File (AI)", "Inserimento Manuale"])
    
    if scelta == "Carica File (AI)":
        file_ven = st.file_uploader("Carica PDF, Foto o XML di Vendita", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'], key="up_ven")
        if file_ven and st.button("🔍 ANALIZZA VENDITA"):
            d = analizza_documento(file_ven, "VENDITA")
            if d:
                payload = {"tipo": "VENDITA", "soggetto": d[0], "data_doc": d[1], "totale": d[2], "imponibile": d[3], "iva": d[4], "scadenza": d[5], "note": d[6]}
                if requests.post(WEBHOOK_URL, json=payload).status_code == 200:
                    st.success(f"Vendita a {d[0]} salvata!")
                    st.balloons()
    else:
        with st.form("vendita_manuale"):
            c = st.text_input("Cliente")
            t = st.number_input("Totale (€)", min_value=0.0)
            sc = st.date_input("Scadenza")
            n = st.text_area("Articoli")
            if st.form_submit_button("💾 SALVA MANUALE"):
                imp = t / 1.22
                payload = {"tipo": "VENDITA", "soggetto": c, "data_doc": str(datetime.now().date()), "totale": t, "imponibile": round(imp, 2), "iva": round(t-imp, 2), "scadenza": str(sc), "note": n}
                requests.post(WEBHOOK_URL, json=payload)
                st.success("Vendita registrata!")

if st.sidebar.button("🚪 Logout"):
    st.session_state['auth'] = False
    st.rerun()
