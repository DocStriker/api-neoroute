import unicodedata
import time
import requests

class Utils:

    def remove_acentos(self, texto):
        """entrada: 'texto' -> 'string', saída: 'string' normalizada sem acentos."""
        if not texto:
            return ""
        # Normaliza para NFD (separa caracteres + acentos)
        nfkd = unicodedata.normalize('NFD', texto)
        # Remove caracteres não-ASCII (acentos)
        return "".join([c for c in nfkd if not unicodedata.combining(c)])
    
    def extract_adress(self, json):
        """recebe um json e retorna uma string."""
        adress = f"{json['street']}, {json['city'] + ', 'if json['city'] else ''}{json['state']}"

        return adress # Retorno em string
    
    def safe_request(self, url, params):
        delay = 6  # tempo inicial de espera entre tentativas (em segundos)

        for i in range(5):
            try:
                response = requests.get(url, params=params, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception as e:
                print(f"Tentativa {i+1} falhou:", e)
                time.sleep(delay)
                delay *= 2  # backoff exponencial

    def normalize_agent_response(self, r: dict) -> dict:
        return {
            "street": r.get("street", ""),
            "city": r.get("city", ""),
            "state": r.get("state", ""),
            "cargo_type": r.get("cargo_type", ""),
        }

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def wait(self):
        now = time.time()

        # remove chamadas antigas
        self.calls = [t for t in self.calls if now - t < self.period]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            time.sleep(max(sleep_time, 0))

        self.calls.append(time.time())