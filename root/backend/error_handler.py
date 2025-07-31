import logging
import time
from functools import wraps
import requests

# 🔧 Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="app.log",
    filemode="a"
)

def log_error(message, exc=None):
    if exc:
        logging.error(message, exc_info=True)
    else:
        logging.error(message)

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

# 🔁 Smarte Retry-Logik mit Exponential Backoff
def smart_retry(
    max_retries=6,
    base_delay=60,
    backoff_factor=2,
    allowed_status_codes=(429, 504),
    exceptions=(requests.exceptions.RequestException,),
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    response = func(*args, **kwargs)

                    # Wenn Funktion ein requests.Response zurückgibt:
                    if isinstance(response, requests.Response):
                        if response.status_code in allowed_status_codes:
                            log_warning(f"HTTP {response.status_code} – Versuch {attempt}/{max_retries}. Warte {delay}s …")
                            time.sleep(delay)
                            delay *= backoff_factor
                            continue
                        response.raise_for_status()  # andere Fehler auslösen
                        return response
                    return response

                except exceptions as e:
                    log_warning(f"Fehler beim Versuch {attempt}: {e}. Warte {delay}s …")
                    if attempt == max_retries:
                        log_error("Maximale Anzahl Wiederholungen erreicht. Abbruch.", e)
                        raise
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
