Perfetto! Ecco il codice completo per trasformare la tua app in una Dashboard Professionale Dark Style, proprio come nell'immagine.

Ho aggiunto:

Tema Scuro (Dark Mode): Sfondo blu notte e card eleganti.

Grafici: Un grafico a torta che mostra la distribuzione dei costi (Imponibile vs IVA).

Tabella Dettagliata: Una visualizzazione pulita di tutti i dati estratti (niente più JSON brutto da vedere).

Metriche in evidenza: Fornitore, Data e Totale messi in risalto in alto.

🛠️ Codice Completo da copiare in main.py
Python

import streamlit as st
import requests
import base64
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI Invoice Dashboard", page_icon="📊", layout="wide")

# --- STILE CSS DARK DASHBOARD ---
st.markdown("""
    <style>
    /* Sfondo totale scuro */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Card dei risultati */
    .metric-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
    }
    /* Login Box */
    .login-box {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: #161b22;
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    /* Bottoni */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #238636;
        color: white;
        border: none;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAZIONE API ---
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    st.error("Manca API_KEY nei Secrets!")
    st.stop()

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>📊 Dashboard Login</h2>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u == "admin" and p == "tuapassword":
            st.session_state['auth'] = True
            st.session_state['user'] = u
            st.rerun()
        else: st.error("Accesso negato")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- APP PRINCIPALE ---
st.title("📊 Dashboard Analisi Fatture AI")
st.markdown("---")

# Sidebar per caricamento
with st.sidebar:
    st.header("⚙️ Operazioni")
    file = st.file_uploader("Carica Documento (PDF/JPG)", type=['pdf', 'jpg', 'jpeg', 'png'])
    if st.button("Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    if st.button("🔍 AVVIA ANALISI"):
        try:
            with st.spinner("Analisi intelligente in corso..."):
                # 1. Recupero modello v1
                list_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
                list_res = requests.get(list_url).json()
                target_model = next((m['name'] for m in list_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])), "models/gemini-1.5-flash")

                # 2. Preparazione dati
                file_data = base64.b64encode(file.read()).decode("utf-8")
                mime_type = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                # 3. Prompt per dati strutturati
                url = f"https://generativelanguage.googleapis.com/v1/{target_model}:generateContent?key={API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Estrai questi dati: Fornitore, Data, Totale, Imponibile, IVA. Rispondi solo con i valori separati da virgola in quest'ordine."},
                            {"inline_data": {"mime_type": mime_type, "data": file_data}}
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload)
                raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                dati = [d.strip() for d in raw_text.split(',')]

                # Visualizzazione Metric Cards
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">🏢 FORNITORE</div><div class="metric-value">{dati[0]}</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">📅 DATA</div><div class="metric-value">{dati[1]}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">💰 TOTALE</div><div class="metric-value">{dati[2]} €</div></div>', unsafe_allow_html=True)

                st.markdown("### 📈 Dettagli e Visualizzazione")
                
                col_chart, col_table = st.columns([1, 1.5])
                
                # Grafico a torta
                with col_chart:
                    try:
                        imp = float(dati[3].replace('€','').replace(',','.'))
                        iva = float(dati[4].replace('€','').replace(',','.'))
                        fig = go.Figure(data=[go.Pie(labels=['Imponibile', 'IVA'], values=[imp, iva], hole=.3, marker_colors=['#58a6ff', '#238636'])])
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.warning("Dati numerici non sufficienti per il grafico")

                # Tabella Dettagli
                with col_table:
                    df = pd.DataFrame({
                        "Campo": ["Fornitore", "Data", "Imponibile", "IVA", "Totale"],
                        "Valore": dati
                    })
                    st.table(df)
                
                st.balloons()

        except Exception as e:
            st.error(f"Errore: {e}")
else:
    st.info("👋 Benvenuto! Carica un file nella barra laterale per iniziare la scansione.")

# --- DASHBOARD BOT AGGIORNATA ---
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Stato Bot")
st.sidebar.write("**Valore:** 13,82 USDT")
st.sidebar.write("**Diff:** -619,84 USDT")
