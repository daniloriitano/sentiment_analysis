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
        "https://www.liberoquotidiano.it/news/politica/33193452/l-ultima-parola-giorgia-meloni-enrico-mentana-fascismo-ancora-sinistra.html",
        "https://www.liberoquotidiano.it/news/politica/33194095/giorgia-meloni-wsj-pragmatica-perche-vincera.html",
        "https://www.liberoquotidiano.it/news/personaggi/33202699/giorgia-meloni-emanuele-trevisempre-qualche-fascista-accontentare.html",
        "https://www.liberoquotidiano.it/news/politica/33203780/giorgia-meloni-costretta-rinviare-voto-caos-seggio.html",
        "https://www.liberoquotidiano.it/video/politica/33205493/giorgia-meloni-presidente-seggio-cosa-succedera-questa-sera.html"
    ],
    "Lega": [
        "https://www.liberoquotidiano.it/news/politica/33190643/zona-bianca-matteo-salvini-mia-ragione-vita.html",
        "https://www.liberoquotidiano.it/news/politica/33194108/matteo-salvini-bollette-bloccate-prima-cosa-faremo-governo.html",
        "https://www.liberoquotidiano.it/news/politica/33208738/elezioni-2022-segui-risultati-in-diretta.html",
        "https://www.liberoquotidiano.it/news/personaggi/33204868/matteo-salvini-oroscopo-elezioni-2022-profezia-cupa.html",
        "https://www.liberoquotidiano.it/news/politica/33209008/matteo-salvini-ce-l-ho-in-testa-frase-fa-impazzire-repubblica.html"
    ],
    "Movimento 5 Stelle": [
        "https://www.liberoquotidiano.it/news/spettacoli/televisione/33190640/mentana-gela-conte-non-tiri-fuori-pentole-imbarazzo-reazione.html",
        "https://www.liberoquotidiano.it/news/personaggi/33196321/marco-travaglio-cogl-oro-fatto-quotidiano-difesa-m5s-giuseppe-conte.html",
        "https://www.liberoquotidiano.it/news/personaggi/33195209/enrico-mentana-giuseppe-conte-perche-cosi-contento-gelo-diretta.html",
        "https://www.liberoquotidiano.it/news/politica/33194257/giuseppe-conte-piano-segreto-perche-punta-quirinale.html",
        "https://www.liberoquotidiano.it/news/politica/33209522/affluenza-crollo-sud-giuseppe-conte-trema-centrodestra-scenari-clamorosi.html"
    ],
    "Partito Democratico": [
        "https://www.liberoquotidiano.it/news/personaggi/33199248/giuseppe-cruciani-umilia-pd-sinistri-depressi-distrutti-godo.html",
        "https://www.liberoquotidiano.it/news/personaggi/33213813/giuliano-ferrara-contro-pd-carlo-calenda-armata-brancaleone.html",
        "https://www.liberoquotidiano.it/news/politica/33217357/emanuele-fiano-umiliato-isabella-rauti-sesto-san-giorvanni.html",
        "https://www.liberoquotidiano.it/news/politica/33217294/elezioni-2022-giorgia-meloni-rovina-sinistra-restano-solo-barricate.html",
        "https://www.liberoquotidiano.it/news/politica/33218964/pd-emanuele-fiano-enrico-letta-non-poteva-che-finire-cosi.html"
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
    df.to_csv("risultati_sentiment_liberoquotidiano.csv", index=False, encoding="utf-8")
    print("✅ Analisi completata! Dati salvati in 'risultati_sentiment_ilgiornale.csv'")

# Esegui il codice
if __name__ == "__main__":
    main()
