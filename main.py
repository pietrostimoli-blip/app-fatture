import streamlit as st
import requests
import base64
import plotly.graph_objects as go

# --- CONFIGURAZIONE GRAFICA ---
st.set_page_config(page_title="Scanner AI Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .metric-card { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 15px; }
    .m-label { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; }
    .m-value { color: #58a6ff; font-size: 1.6rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.write("# 🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Entra"):
            if u == "admin" and p == "tuapassword":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# --- APP ---
st.title("📊 Analisi Documenti")

with st.sidebar:
    file = st.file_uploader("Carica file (PDF/JPG)", type=['pdf', 'jpg', 'jpeg', 'png'])
    if st.button("🚪 Esci"):
        st.session_state['auth'] = False
        st.rerun()

if file:
    if st.button("🔍 ANALIZZA ORA"):
        try:
            with st.spinner("Ricerca modello compatibile..."):
                KEY = st.secrets["API_KEY"]
                
                # 1. SCOPRIAMO QUALE MODELLO PUOI USARE (Per evitare il 404)
                list_url = f"https://generativelanguage.googleapis.com/v1/models?key={KEY}"
                models_data = requests.get(list_url).json()
                
                # Cerchiamo un modello Gemini (Pro o Flash) disponibile
                try:
                    target_model = [m['name'] for m in models_data['models'] 
                                  if 'generateContent' in m['supportedGenerationMethods']][-1]
                except:
                    st.error("Nessun modello trovato per questa API KEY. Creane una nuova in un 'New Project' su Google AI Studio.")
                    st.stop()

                # 2. PREPARAZIONE FILE
                file_b64 = base64.b64encode(file.read()).decode("utf-8")
                mime = "application/pdf" if file.type == "application/pdf" else "image/jpeg"
                
                # 3. CHIAMATA DINAMICA
                url = f"https://generativelanguage.googleapis.com/v1/{target_model}:generateContent?key={KEY}"
                payload = {
                    "contents": [{"parts": [
                        {"text": "Estrai Fornitore, Data, Totale, Imponibile, IVA separati da virgola. Se non sai scrivi 0."},
                        {"inline_data": {"mime_type": mime, "data": file_b64}}
                    ]}]
                }
                
                response = requests.post(url, json=payload)
                res_json = response.json()
                
                if response.status_code == 200:
                    testo = res_json['candidates'][0]['content']['parts'][0]['text']
                    d = [item.strip() for item in testo.split(',')]
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="metric-card"><div class="m-label">Fornitore</div><div class="m-value">{d[0]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-card"><div class="m-label">Data</div><div class="m-value">{d[1]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-card"><div class="m-label">Totale</div><div class="m-value">{d[2]} €</div></div>', unsafe_allow_html=True)
                    
                    with c2:
                        try:
                            v_imp = float(d[3].replace(',','.'))
                            v_iva = float(d[4].replace(',','.'))
                            fig = go.Figure(data=[go.Pie(labels=['Netto', 'IVA'], values=[v_imp, v_iva], hole=.4)])
                            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                            st.plotly_chart(fig)
                        except:
                            st.warning("Grafico non disponibile per dati non numerici.")
                    st.balloons()
                else:
                    st.error(f"Errore Google: {res_json['error']['message']}")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
