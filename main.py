Hai ragione, scusami. Il problema è che nel codice precedente il sistema di controllo cercava di verificare le credenziali in modo rigido.

Ho riscritto il sistema di login per renderlo multi-utente e semplicissimo: ora puoi aggiungere tutti i nomi e le password che vuoi in una lista chiara all'inizio del programma.

🛠️ Codice Completo con Login Multi-Utente
Copia questo codice in main.py. Ho inserito 4 utenti diversi come esempio (admin, ufficio, negozio1, magazzino). Puoi cambiarli o aggiungerne altri nella sezione UTENTI_AUTORIZZATI.

Python

import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Configurazione Pagina
st.set_page_config(page_title="AI Business Dashboard", layout="wide")

# 2. Configurazione Link Google Sheets (Web App URL)
# Ricordati di incollare qui il tuo link che finisce con /exec
WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_APPS_SCRIPT"

# 3. 🔐 LISTA UTENTI E PASSWORD (Aggiungi qui chi vuoi)
UTENTI_AUTORIZZATI = {
    "admin": "12345",
    "ufficio": "ufficio2025",
    "negozio1": "scelta1",
    "magazzino": "pezzi2025"
}

# --- STILE GRAFICO ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .login-card { 
        background: #161b22; 
        padding: 30px; 
        border-radius: 15px; 
        border: 1px solid #30363d;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3em; }
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
        
        # Campi input
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        
        if st.button("ACCEDI"):
            # Controllo se l'utente esiste e la password combacia
            if user_input in UTENTI_AUTORIZZATI and UTENTI_AUTORIZZATI[user_input] == pass_input:
                st.session_state['auth'] = True
                st.session_state['user_attivo'] = user_input
                st.rerun()
            else:
                st.error("❌ Username o Password errati.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACCIA PRINCIPALE (Se il login è ok) ---
st.title("📊 AI Business Management")
st.markdown(f"Benvenuto, **{st.session_state['user_attivo']}** | Database Cloud Connesso ✅")

# Menu a schede
tab1, tab2 = st.tabs(["📥 ACQUISTI / FORNITORI", "📤 VENDITE / CLIENTI"])

with tab1:
    st.subheader("Scanner Fatture Acquisto")
    file_acq = st.file_uploader("Carica Foto, PDF o XML", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'])
    
    if file_acq and st.button("🔍 ANALIZZA E ARCHIVIA"):
        with st.spinner("L'AI sta leggendo i dati..."):
            try:
                API_KEY = st.secrets["API_KEY"]
                file_bytes = file_acq.read()
                
                # Prompt per estrarre tutto, inclusi articoli e scadenze
                prompt = "Estrai Fornitore, DataDocumento, Totale, Imponibile, IVA, Scadenza, ElencoArticoli. Rispondi SOLO con i valori separati da virgola."
                
                if file_acq.name.lower().endswith('.xml'):
                    payload = {"contents": [{"parts": [{"text": f"{prompt}\n{file_bytes.decode('utf-8')}"}]}]}
                else:
                    file_b64 = base64.b64encode(file_bytes).decode("utf-8")
                    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": file_acq.type, "data": file_b64}}]}]}
                
                res = requests.post(f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}", json=payload).json()
                d = [item.strip() for item in res['candidates'][0]['content']['parts'][0]['text'].split(',')]
                while len(d) < 7: d.append("N/D")

                # Allineamento con le tue colonne (Tipo, DataIniz, Soggetto, DataDoc, Totale, Imponibile, IVA, Scadenza, Note)
                payload_sheets = {
                    "tipo": "ACQUISTO",
                    "soggetto": d[0],
                    "data_doc": d[1],
                    "totale": d[2],
                    "imponibile": d[3],
                    "iva": d[4],
                    "scadenza": d[5],
                    "note": f"Articoli: {d[6]} | Operatore: {st.session_state['user_attivo']}"
                }
                
                req = requests.post(WEBHOOK_URL, json=payload_sheets)
                if req.status_code == 200:
                    st.success(f"✅ Archiviato: {d[0]} ({d[2]}€)")
                    st.balloons()
            except Exception as e:
                st.error(f"Errore tecnico: {e}")

with tab2:
    st.subheader("Registrazione Fattura Vendita")
    with st.form("form_vendita"):
        cliente = st.text_input("Nome Cliente")
        tot_v = st.number_input("Totale Fattura (€)", min_value=0.0)
        scad_v = st.date_input("Scadenza Pagamento")
        articoli_v = st.text_area("Descrizione Articoli/Servizi")
        
        if st.form_submit_button("💾 SALVA VENDITA"):
            imp_v = tot_v / 1.22
            p_sheets = {
                "tipo": "VENDITA",
                "soggetto": cliente,
                "data_doc": str(datetime.now().date()),
                "totale": tot_v,
                "imponibile": round(imp_v, 2),
                "iva": round(tot_v - imp_v, 2),
                "scadenza": str(scad_v),
                "note": articoli_v
            }
            requests.post(WEBHOOK_URL, json=p_sheets)
            st.success("✅ Vendita registrata nel Cloud!")

with st.sidebar:
    st.markdown(f"👤 Utente: **{st.session_state['user_attivo']}**")
    if st.button("🚪 Logout"):
        st.session_state['auth'] = False
        st.rerun()
    st.markdown("---")
    st.markdown(f"🔗 [Apri Google Sheets](https://docs.google.com/spreadsheets/d/13Y
