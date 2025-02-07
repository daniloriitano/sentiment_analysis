import time
import pandas as pd
import nltk
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from nltk.sentiment import SentimentIntensityAnalyzer

# Scarica il dizionario per l'analisi del sentiment (VADER)
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Funzione per rimuovere il testo indesiderato
def rimuovi_testo_indesiderato(testo):
    pattern = r"(Il rispetto della tua riservatezza è la nostra priorità.*?questo sito web e v|SOSTIENICI|Community|Abbonati|Accedi|Leggi anche|SEGUI SU|Condividi|ISCRIVITI)"
    return re.sub(pattern, '', testo, flags=re.IGNORECASE).strip()

# Dizionario con i partiti e i relativi articoli aggiornati
articoli = {
    "Fratelli d’Italia": [
        "https://www.open.online/2022/07/19/governo-meloni-ministri-vittoria-elezioni-fdi/",
        "https://www.open.online/2022/08/27/elezioni-politiche-2022-meloni-premier-mattarella/",
        "https://www.open.online/2022/08/30/elezioni-politiche-2022-di-maio-governo-meloni-draghi/",
        "https://www.open.online/2022/08/31/elezioni-politiche-2022-elsa-fornero-giorgia-meloni-premier/",
        "https://www.open.online/2022/09/24/elezioni-politiche-2022-cantante-cosmo-vs-meloni/"
    ],
    "Lega": [
        "https://www.open.online/2022/07/23/giorgia-meloni-governo-regola-vs-centrodestra/",
        "https://www.open.online/2022/07/25/elezioni-2022-centrodestra-piano-salvini-berlusconi-vs-meloni/",
        "https://www.open.online/2022/07/25/botta-e-risposta-meloni-salvini-premiership-centrodestra/",
        "https://www.open.online/2022/08/30/elezioni-politiche-2022-salvini-decreti-sicurezza-sbarchi/",
        "https://www.open.online/2022/09/24/elezioni-politiche-2022-possibili-risultati-tre-scenari/"
    ],
    "Partito Democratico": [
        "https://www.open.online/2022/07/21/crisi-di-governo-draghi-partito-democratico/",
        "https://www.open.online/2022/07/22/elezioni-pd-letta-renzi-m5s-sala-di-maio/",
        "https://www.open.online/2022/07/22/elezioni-regionali-primarie-sicilia-conte-vs-letta/",
        "https://www.open.online/2022/07/23/elezioni-sondaggi-collegi-maggioritari-perche/",
        "https://www.open.online/2022/07/28/elezioni-2022-meloni-fdi-vs-pd-ucraina/"
    ],
    "Movimento 5 Stelle": [
        "https://www.open.online/2022/07/23/conte-crisi-governo-m5s-forza-leale/",
        "https://www.open.online/2022/07/23/m5s-conte-vs-letta-elezioni/",
        "https://www.open.online/2022/07/24/letta-rottura-m5s-irreversibile/",
        "https://www.open.online/2022/07/25/elezioni-politiche-sondaggio-swg-25-luglio-2022/",
        "https://www.open.online/2022/07/26/m5s-piano-alleanza-sinistra-melenchon/"
    ]
}


# Configura WebDriver
def configura_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("user-agent=Mozilla/5.0")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Estrai testo con Selenium
def estrai_testo(url, driver):
    print(f"📰 Analizzando: {url}")
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        testo = driver.execute_script("return document.body.innerText")
        return rimuovi_testo_indesiderato(testo)
    except Exception as e:
        print(f"❌ Errore estrazione: {e}")
        return ""

# Funzione per ottenere il sentiment con VADER
def analizza_sentiment(testo):
    if not testo:
        return "Neutro", 0  

    punteggio = sia.polarity_scores(testo)['compound']

    if punteggio > 0.85:
        tono = "Positivo Forte"
    elif punteggio > 0.55:
        tono = "Positivo"
    elif punteggio > 0.2:
        tono = "Neutro"
    elif punteggio > -0.55:
        tono = "Negativo"
    else:
        tono = "Negativo Forte"

    punteggio_normalizzato = (punteggio + 1) / 2  # Normalizzazione tra 0 e 1
    print(f"📊 SENTIMENT: {tono} ({punteggio_normalizzato})\n")
    return tono, punteggio_normalizzato

# Funzione principale
def main():
    risultati = []
    driver = configura_driver()

    try:
        for partito, urls in articoli.items():
            for url in urls:
                testo = estrai_testo(url, driver)
                tono, punteggio = analizza_sentiment(testo)
                risultati.append({
                    "Partito": partito,
                    "URL": url,
                    "Tono": tono,
                    "Punteggio": punteggio,
                    "Testo": testo[:1000]  # Salviamo solo i primi 1000 caratteri
                })
    finally:
        driver.quit()

    # Salva tutti i risultati in un unico file CSV
    percorso_csv = "/Users/daniloriitano/Sentiment_Analysis/Project Folder/risultati_sentiment_open.csv"
    df = pd.DataFrame(risultati)
    df.to_csv(percorso_csv, index=False, encoding="utf-8")
    print(f"✅ Analisi completata! Dati salvati in '{percorso_csv}'")

# Esegui il codice
if __name__ == "__main__":
    main()

