import streamlit as st
import requests
import base64
from datetime import datetime

# CONFIGURAZIONE
st.set_page_config(page_title="AI Business Dashboard Pro", layout="wide")
WEBHOOK_URL = "IL_TUO_URL_DI_APPS_SCRIPT" 
UTENTI = {"admin": "pass123", "ufficio": "ufficio2025"}

# LOGIN
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("### 🔐 Accesso Gestionale Cloud")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ENTRA"):
            if u in UTENTI and UTENTI[u] == p:
                st.session_state['auth'] = True
                st.session_state['user'] = u
                st.rerun()
    st.stop()

st.title("🚀 AI Business Manager")
tab1, tab2 = st.tabs(["📥 ACQUISTI & ARTICOLI", "📤 VENDITE"])

# --- TAB ACQUISTI ---
with tab1:
    st.subheader("Scanner Intelligente (Riconoscimento Articoli e Scadenze)")
    up_acq = st.file_uploader("Carica Fattura Fornitore (Foto, PDF, XML)", type=['pdf', 'jpg', 'jpeg', 'png', 'xml'])
    
    if up_acq and st.button("🔍 ANALIZZA E ARCHIVIA"):
        with st.spinner("L'AI sta analizzando articoli e scadenze..."):
            API_KEY = st.secrets["API_KEY"]
            file_bytes = up_acq.read()
            
            # PROMPT POTENZIATO PER SCADENZE E ARTICOLI
            prompt = """Estrai questi dati separati da virgola: 
            1.Soggetto, 2.DataDoc, 3.Totale, 4.Imponibile, 5.IVA, 6.ScadenzaPagam, 7.ElencoArticoli abbreviato.
            Se mancano scrivi 0 o N/D."""
            
            if up_acq.name.lower().endswith('.xml'):
                payload_ai = {"contents": [{"parts": [{"text": f"{prompt}\n{file_bytes.decode('utf-8')}"}]}]}
            else:
                payload_ai = {"contents": [{"parts": [{"text": prompt}, 
                             {"inline_data": {"mime_type": up_acq.type, "data": base64.b64encode(file_bytes).decode("utf-8")}}]}]}
            
            res_ai = requests.post(f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}", json=payload_ai).json()
            d = [item.strip() for item in res_ai['candidates'][0]['content']['parts'][0]['text'].split(',')]
            
            # Allineamento con le tue colonne del foglio
            p_sheets = {
                "tipo": "ACQUISTO",
                "soggetto": d[0],
                "data_doc": d[1],
                "totale": d[2],
                "imponibile": d[3],
                "iva": d[4],
                "scadenza": d[5],
                "note": d[6] # Qui finiscono gli articoli letti dall'AI
            }
            
            requests.post(WEBHOOK_URL, json=p_sheets)
            st.success(f"Archiviato: {d[0]} | Scadenza: {d[5]}")
            st.info(f"Articoli rilevati: {d[6]}")

# --- TAB VENDITE ---
with tab2:
    st.subheader("Nuova Vendita")
    with st.form("v_manuale"):
        cliente = st.text_input("Cliente")
        t_v = st.number_input("Totale (€)", min_value=0.0)
        scad_v = st.date_input("Scadenza Pagamento")
        desc_v = st.text_area("Articoli Venduti / Descrizione")
        if st.form_submit_button("✅ REGISTRA VENDITA"):
            imp = t_v / 1.22
            requests.post(WEBHOOK_URL, json={
                "tipo": "VENDITA", "soggetto": cliente, "data_doc": str(datetime.now().date()),
                "totale": t_v, "imponibile": round(imp, 2), "iva": round(t_v-imp, 2),
                "scadenza": str(scad_v), "note": desc_v
            })
            st.success("Vendita registrata!")
