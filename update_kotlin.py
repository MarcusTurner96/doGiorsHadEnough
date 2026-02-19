import requests
from bs4 import BeautifulSoup
import re
import os

# --- CONFIGURAZIONE ---
CHANNEL_USERNAME = "Streaming_community_sito" 
FILE_PATH = "src/StreamingCommunity/src/main/kotlin/it/dogior/hadEnough/StreamingCommunity.kt"

def get_latest_url_from_telegram():
    url_tg = f"https://t.me/s/{CHANNEL_USERNAME}"
    try:
        response = requests.get(url_tg, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        if not messages:
            return None

        # Prende l'ultimo messaggio e pulisce i <br/>
        last_msg = messages[-1]
        for br in last_msg.find_all("br"):
            br.replace_with("\n")
        
        lines = [l.strip() for l in last_msg.get_text().split('\n') if l.strip()]
        
        if lines:
            # Estrae l'ultima riga e pulisce eventuali spazi o protocolli
            raw_domain = lines[-1].replace("https://", "").replace("http://", "").split()[0]
            return raw_domain
        return None
    except Exception as e:
        print(f"Errore Telegram: {e}")
        return None

def update_kotlin_file(new_domain):
    if not os.path.exists(FILE_PATH):
        print(f"File non trovato: {FILE_PATH}")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex per trovare la riga: cerca 'val mainUrl = "https://.../"'
    # Gestisce spazi variabili e diversi contenuti tra le virgolette
    pattern = r'(val\s+mainUrl\s*=\s*"https://)(.*?)(/")'
    new_content = re.sub(pattern, rf'\1{new_domain}\3', content)

    if content == new_content:
        print("L'URL è già aggiornato o la variabile non è stata trovata.")
    else:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        print(f"File aggiornato con il dominio: {new_domain}")

if __name__ == "__main__":
    domain = get_latest_url_from_telegram()
    if domain:
        update_kotlin_file(domain)
