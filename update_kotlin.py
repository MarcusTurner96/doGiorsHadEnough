import requests
from bs4 import BeautifulSoup
import re
import os

# --- CONFIGURAZIONE ---
CHANNEL_USERNAME = "Streaming_community_sito"  # <--- Inserisci qui il nome del tuo canale Telegram
FILE_PATH = "src/StreamingCommunity/src/main/kotlin/it/dogior/hadEnough/StreamingCommunity.kt"

def get_latest_url_from_telegram():
    url_tg = f"https://t.me/s/{CHANNEL_USERNAME}"
    try:
        response = requests.get(url_tg, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        if not messages:
            return None

        # Pulisce i <br/> per leggere correttamente le righe
        last_msg = messages[-1]
        for br in last_msg.find_all("br"):
            br.replace_with("\n")
        
        lines = [l.strip() for l in last_msg.get_text().split('\n') if l.strip()]
        
        if lines:
            # Estrae l'ultima riga ripulendola da protocolli ed eventuali spazi
            raw_domain = lines[-1].replace("https://", "").replace("http://", "").split()[0]
            # Assicura che finisca con lo slash finale (es. https://sito.fun/)
            if not raw_domain.endswith("/"):
                raw_domain += "/"
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

    # --- REGEX AGGIORNATA PER LA NUOVA STRUTTURA ---
    # Cerca la riga: const val DEFAULT_BASE_URL = "https://..."
    pattern = r'(const\s+val\s+DEFAULT_BASE_URL\s*=\s*"https?://)(.*?)(/")'
    
    new_content, count = re.subn(pattern, rf'\1{new_domain.rstrip("/")}\3', content)

    if count == 0:
        print("ATTENZIONE: Nessuna corrispondenza trovata per DEFAULT_BASE_URL nel file Kotlin.")
    elif content == new_content:
        print("L'URL è già aggiornato nel file Kotlin.")
    else:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"File aggiornato con successo con il dominio: {new_domain}")

if __name__ == "__main__":
    print("Avvio lettura Telegram...")
    domain = get_latest_url_from_telegram()
    print(f"Dominio estratto da Telegram: {domain}")
    if domain:
        update_kotlin_file(domain)
    else:
        print("ATTENZIONE: Nessun dominio valido estratto o messaggio vuoto.")
