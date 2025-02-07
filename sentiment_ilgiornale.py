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
        "https://www.ilgiornale.it/news/politica/centrodestra-lavoro-sar-governo-pi-politico-sempre-2074772.html",
        "https://www.ilgiornale.it/news/politica/abbiamo-rotto-schemi-e-creato-cortocircuiti-nella-sinistra-2074340.html",
        "https://www.ilgiornale.it/news/politica/lezione-democrazie-pure-monde-fa-chapeau-meloni-2072525.html",
        "https://www.ilgiornale.it/news/milano/centrodestra-sopra-50-e-fdi-primo-lombardia-2070332.html",
        "https://www.ilgiornale.it/news/politica/lezione-democrazie-pure-monde-fa-chapeau-meloni-2072525.html"
    ],
    "Lega": [
        "https://www.ilgiornale.it/news/politica/fallimento-letta-vittoria-salvini-cos-basi-scelgono-loro-2073711.html",
        "https://www.ilgiornale.it/speciali/elezioni-politiche-2022-166972.html",
        "https://www.ilgiornale.it/news/politica/elezioni-politiche-ecco-14-liste-eliminate-c-anche-palamara-2059404.html",
        "https://www.ilgiornale.it/news/politica/uninominale-camera-e-senato-ecco-tutti-i-nomi-lega-2060160.html",
        "https://www.ilgiornale.it/news/politica/si-tira-dritto-cinque-anni-giorgia-gi-parliamo-squadra-2070128.html"
    ],
    "Movimento 5 Stelle": [
        "https://www.ilgiornale.it/news/politica/senza-rdc-viene-terza-guerra-mondiale-cos-sud-hanno-votato-2072070.html",
        "https://www.ilgiornale.it/news/politica/elezioni-2022-seggi-chiusi-spoglio-2069928.html",
        "https://www.ilgiornale.it/news/politica/programma-politico-movimento-cinque-stelle-2061451.html",
        "https://www.ilgiornale.it/news/politica/m5s-giallo-parlamentarie-conte-nasconde-i-candidati-2059682.html",
        "https://www.ilgiornale.it/news/politica/m5s-passa-allincasso-35-milioni-elettori-comprati-reddito-2063540.html"
    ],
    "Partito Democratico": [
        "https://www.ilgiornale.it/news/politica/lingenua-opposizione-2074488.html",
        "https://www.ilgiornale.it/news/politica/attacco-democrazia-blitz-pd-sulle-nomine-cos-occupa-tutte-2074156.html",
        "https://www.ilgiornale.it/news/politica/liste-letta-fanno-infuriare-pd-amici-catapultati-nei-fortini-2059676.html",
        "https://www.ilgiornale.it/news/politica/pd-partito-ztl-ormai-fuori-realt-2070351.html",
        "https://www.ilgiornale.it/news/politica/ci-aspetta-questo-ancora-fake-news-contro-meloni-sinistra-2074377.html"
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

    punteggio_normalizzato = (punteggio + 1) / 2  
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
                    "Punteggio": punteggio
                })
    finally:
        driver.quit()

    # Salva tutti i risultati in un unico file CSV
    percorso_csv = "/Users/daniloriitano/Sentiment_Analysis/Project Folder/risultati_sentiment_ilgiornale.csv"
    df = pd.DataFrame(risultati)
    df.to_csv(percorso_csv, index=False, encoding="utf-8")
    print(f"✅ Analisi completata! Dati salvati in '{percorso_csv}'")

# Esegui il codice
if __name__ == "__main__":
    main()

