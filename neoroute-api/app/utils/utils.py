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
        delay = 5

        for i in range(5):
            try:
                response = requests.get(url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception as e:
                print(f"Tentativa {i+1} falhou:", e)
                time.sleep(delay)
                delay *= 2  # backoff exponencial

    def normalize_agent_response(self, r: dict) -> dict:
        return {
            "street": r.get("street") or "",
            "city": r.get("city") or "",
            "state": r.get("state") or "",
            "cargo_type": r.get("cargo_type") or "",
        }