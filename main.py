L'errore 'candidates' si verifica quando l'AI non riesce a generare una risposta (magari perché il file è sfocato o il formato non è chiaro) e il codice cerca di leggere un risultato che non esiste.

Ho riscritto il codice per risolvere questo bug e, come richiesto, ho rimosso tutte le informazioni relative ai bot. Ora l'interfaccia è pulita, scura e focalizzata solo sulla tua analisi finanziaria con grafici professionali.

🛠️ Codice Completo "Clean Dark Dashboard"
Copia questo in main.py. Assicurati di avere il file requirements.txt con dentro plotly e pandas come indicato prima.

Python

import streamlit as st
import requests
import base64
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Financial Scanner", page_icon="📊", layout="wide")

# --- CSS DARK STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .metric-card {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
    }
    .m-label { color: #8b949e; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .m-value { color: #58a6ff; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
    .login-box {
        max-width: 420px;
        margin: 100px auto;
        padding: 40px;
        background: #161b22;
        border-radius: 16px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📑 Scanner Login</h2>", unsafe_allow_html=True)
    u = st.text_input("User")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Accesso Negato")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- INTERFACCIA PRINCIPALE ---
st.title("📊 Dashboard Analisi Documenti")
st.markdown("---")

with st.sidebar:
    st.header("📂 Caricamento")
    file = st.file_uploader("Carica Fattura o Ricevuta", type=['pdf', 'jpg', 'jpeg', 'png'])
    st.markdown("---")
    if st.button("🚪 Log Out"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    col_data, col_viz = st.columns([1, 1])
    
    if st.button("🚀 AVVIA ANALISI"):
        try:
            with st.spinner("L'AI sta estraendo i dati..."):
                API_KEY = st.secrets["API_KEY"]
                file_data = base64.b64encode(file.read()).decode("utf-8")
                mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analizza il documento. Restituisci SOLO 5 valori separati da virgola: Fornitore, Data, Totale (solo numero), Imponibile (solo numero), IVA (solo numero). Se un dato manca scrivi 0."},
                            {"inline_data": {"mime_type": mime_type, "data": file_data}}
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload)
                res_json = response.json()

                # GESTIONE ERRORE 'CANDIDATES'
                if 'candidates' in res_json:
                    data_raw = res_json['candidates'][0]['content']['parts'][0]['text'].split(',')
                    
                    # Estrazione e pulizia
                    fornitore = data_raw[0].strip()
                    data_doc = data_raw[1].strip()
                    totale = data_raw[2].strip()
                    imp_val = float(data_raw[3].strip().replace('€','').replace(',','.'))
                    iva_val = float(data_raw[4].strip().replace('€','').replace(',','.'))

                    with col_data:
                        st.markdown(f"""
                            <div class="metric-card"><div class="m-label">🏢 Fornitore</div><div class="m-value">{fornitore}</div></div>
                            <div class="metric-card"><div class="m-label">📅 Data</div><div class="m-value">{data_doc}</div></div>
                            <div class="metric-card" style="border-color: #238636;"><div class="m-label">💰 Totale</div><div class="m-value">{totale} €</div></div>
                        """, unsafe_allow_html=True)

                    with col_viz:
                        if imp_val > 0 or iva_val > 0:
                            fig = go.Figure(data=[go.Pie(labels=['Imponibile', 'IVA'], 
                                                     values=[imp_val, iva_val], 
                                                     hole=.4, 
                                                     marker_colors=['#58a6ff', '#f85149'])])
                            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white",
                                            margin=dict(t=20, b=20, l=20, r=20),
                                            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Dati numerici non rilevati per il grafico.")
                    st.balloons()
                else:
                    st.error("L'AI non è riuscita a leggere il file. Riprova con un'immagine più chiara.")
                    
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
else:
    st.info("👋 Carica un documento nella barra laterale per iniziare.")
