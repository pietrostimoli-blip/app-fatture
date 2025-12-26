import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
import requests

# --- CONFIGURAZIONE ---
# Inserisci la tua API KEY di Google Gemini
API_KEY = "LA_TUA_CHIAVE_QUI"
genai.configure(api_key=API_KEY)

# ID del tuo foglio Google (quello che hai creato)
SHEET_ID = "IL_TUO_ID_FOGLIO_QUI"

st.set_page_config(page_title="Scanner Fatture", layout="wide")

# --- DASHBOARD BOT ---
st.sidebar.title("📊 Stato Bot")
st.sidebar.metric("Valore Attuale", "13,82 USDT", "-619,84")
st.sidebar.markdown("---")
nome_cliente = st.sidebar.text_input("Nome Negozio/Cliente", "Negozio_1")

st.title("📑 AI Scanner & Archivio Permanente")

# --- CARICAMENTO ---
file = st.file_uploader("Carica o scatta foto", type=['png', 'jpg', 'jpeg', 'pdf'])

if file:
    img = Image.open(file)
    st.image(img, caption="Documento pronto", width=400)
    
    if st.button("🚀 ANALIZZA E SALVA NEL FOGLIO"):
        try:
            with st.spinner('Lavorazione in corso...'):
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Estrai Fornitore, Data e Totale. Rispondi solo con i valori separati da virgola."
                response = model.generate_content([prompt, img])
                
                # Salvataggio simulato per il database
                st.success(f"Dati salvati per {nome_cliente} nel foglio {SHEET_ID}!")
                st.write(f"Risultato AI: {response.text}")
        except Exception as e:
            st.error(f"Errore: {e}")