# LOGICA POTENZIATA PER FATTURA ELETTRONICA (XML)
if file.name.lower().endswith('.xml'):
    content = file_bytes.decode("utf-8")
    # Prompt specifico con istruzioni sui tag XML della fattura elettronica
    prompt_text = f"""
    Analizza questo codice XML di una fattura elettronica italiana. 
    Estrai i seguenti dati cercando i tag specifici (es. <Denominazione>, <Data>, <ImportoTotaleDocumento>):
    1. Fornitore (Cerca in CedentePrestatore)
    2. Data (Tag <Data>)
    3. Totale Fattura (Tag <ImportoTotaleDocumento> o somma di imponibile e imposta)
    4. Imponibile (Tag <Imponibile>)
    5. IVA (Tag <Imposta>)
    6. Note (Numero fattura o causale)

    Rispondi SOLO con i valori separati da virgola. Se un valore non esiste, scrivi 0.
    Codice XML:
    {content}
    """
    payload_ai = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }
