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
        "https://www.open.online/2022/08/31/elezioni-politiche-2022-elsa-fornero-giorgia-meloni-premier/",
        "https://www.open.online/2022/08/27/elezioni-politiche-2022-meloni-premier-mattarella/",
        "https://www.open.online/2022/08/30/elezioni-politiche-2022-di-maio-governo-meloni-draghi/",
        "https://www.open.online/2022/09/24/elezioni-politiche-2022-cantante-cosmo-vs-meloni/"
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
    df = pd.DataFrame(risultati)
    df.to_csv("risultati_sentiment_open.csv", index=False, encoding="utf-8")
    print("✅ Analisi completata! Dati salvati in 'risultati_sentiment_ilgiornale.csv'")

# Esegui il codice
if __name__ == "__main__":
    main()
