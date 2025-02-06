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
        "https://www.ilfattoquotidiano.it/2022/08/05/centrodestra-ponte-sullo-stretto-nucleare-ed-elezione-diretta-del-presidente-della-repubblica-la-bozza-del-programma/6753462/",
        "https://www.ilfattoquotidiano.it/2022/08/10/il-segnale-di-meloni-alla-stampa-estera-nessuna-svolta-autoritaria-la-destra-italiana-ha-consegnato-il-fascismo-alla-storia-da-decenni/6759120/",
        "https://www.ilfattoquotidiano.it/2022/08/12/liliana-segre-e-pd-chiedono-a-meloni-di-togliere-la-fiamma-tricolore-dal-simbolo-di-fdi-partiamo-dai-fatti-non-dalle-parole/6760622/",
        "https://www.ilfattoquotidiano.it/2022/09/26/elezioni-politiche-2022-meloni-questa-e-una-notte-di-riscatto-ora-e-il-tempo-della-responsabilita-e-di-unire-gli-italiani/6817030/",
        "https://www.ilfattoquotidiano.it/2022/07/26/elezioni-cosi-le-alleanze-influiranno-sulla-distribuzione-dei-seggi-centrodestra-verso-la-maggioranza-assoluta-in-ogni-caso-le-simulazioni/6743392/"
    ],
    "Partito Democratico": [
        "https://www.ilfattoquotidiano.it/2022/06/14/gli-ex-elettori-m5s-non-perdoneranno-mai-a-di-maio-e-grillo-la-svolta-draghiana/6626849/",
        "https://www.ilfattoquotidiano.it/2022/08/11/elezioni-il-naufragio-del-campo-largo-si-deve-a-conte-ovvio-e-sempre-colpa-del-m5s/6759753/",
        "https://www.ilfattoquotidiano.it/2022/08/04/elezioni-le-proposte-sulleconomia-dallarea-progressista-sono-un-3-a-1-per-il-m5s/6751376/",
        "https://www.ilfattoquotidiano.it/2022/08/09/il-tira-e-molla-sulle-alleanze-penalizza-tutti-i-partiti-coinvolti-cosa-emerge-dai-sondaggi-gradimento-leader-in-testa-meloni-poi-conte/6757079/",
        "https://www.ilfattoquotidiano.it/2022/08/10/elezioni-la-situazione-di-chi-vota-a-sinistra-e-da-psicoanalisi/6757263/"
    ],
    "Movimento 5 Stelle": [
        "https://www.ilfattoquotidiano.it/2022/06/14/gli-ex-elettori-m5s-non-perdoneranno-mai-a-di-maio-e-grillo-la-svolta-draghiana/6626849/",
        "https://www.ilfattoquotidiano.it/2022/08/11/elezioni-il-naufragio-del-campo-largo-si-deve-a-conte-ovvio-e-sempre-colpa-del-m5s/6759753/",
        "https://www.ilfattoquotidiano.it/2022/08/04/elezioni-le-proposte-sulleconomia-dallarea-progressista-sono-un-3-a-1-per-il-m5s/6751376/",
        "https://www.ilfattoquotidiano.it/2022/08/09/il-tira-e-molla-sulle-alleanze-penalizza-tutti-i-partiti-coinvolti-cosa-emerge-dai-sondaggi-gradimento-leader-in-testa-meloni-poi-conte/6757079/",
        "https://www.ilfattoquotidiano.it/2022/08/10/elezioni-la-situazione-di-chi-vota-a-sinistra-e-da-psicoanalisi/6757263/"
    ],
    "Lega": [
        "https://www.ilfattoquotidiano.it/2022/08/19/flat-tax-le-proposte-di-lega-e-forza-italia-costi-enormi-a-beneficio-di-pochi/6759960/",
        "https://www.ilfattoquotidiano.it/2021/09/22/reddito-la-giravolta-di-salvini-non-e-piu-da-abolire-anzi-darlo-ad-alcuni-e-sacrosanto-e-la-raccolta-firme-di-renzi-non-e-mai-partita/6328712/",
        "https://www.ilfattoquotidiano.it/2022/08/18/lega-il-programma-per-le-elezioni-politiche-2022-scarica-il-pdf/6766751/",
        "https://www.ilfattoquotidiano.it/2022/09/26/elezioni-lanalisi-voto-la-lega-torna-ai-vecchi-confini-di-bossi-e-ha-scarso-supporto-nelle-grandi-citta-travaso-di-voti-verso-fdi/6818444/",
        "https://www.ilfattoquotidiano.it/2022/04/05/sondaggi-come-si-sono-comportati-i-leader-sulla-guerra-letta-e-conte-in-testa-salvini-ultimo-draghi-per-il-54-e-poco-efficace/6549421/"
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
    df.to_csv("risultati_sentiment_fattoquotidiano.csv", index=False, encoding="utf-8")
    print("✅ Analisi completata! Dati salvati in 'risultati_sentiment_ilgiornale.csv'")

# Esegui il codice
if __name__ == "__main__":
    main()
