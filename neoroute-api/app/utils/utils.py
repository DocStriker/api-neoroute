import time
import requests
import hashlib
from app.services.ai_service import AIService

class Utils:
    
    def safe_request(self, url, params):
        delay = 6
        
        for i in range(5):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=20,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                if response.status_code != 200:
                    raise requests.RequestException(f"Status {response.status_code}")

                return response

            except requests.RequestException as e:
                print(f"Try {i+1} failed: {e} \n")
                time.sleep(delay)
                delay *= 2

        raise requests.RequestException("Todas as tentativas falharam \n")

    def hash(self, texto):
        return hashlib.md5(texto.encode()).hexdigest()

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.ai = AIService()

    def wait(self):
        now = time.time()

        # remove chamadas antigas
        self.calls = [t for t in self.calls if now - t < self.period]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            time.sleep(max(sleep_time, 0))
            print(f"Rate limit reached. Waiting for {sleep_time:.2f} seconds...")

        self.calls.append(time.time())

    def safe_ai_call(self, texto):
        for i in range(3):
            try:
                self.wait()
                return self.ai.parse(texto, model="openrouter")
            except Exception as e:
                print(f"Erro na chamada da IA (tentativa {i+1}): {e}")
                time.sleep(2 ** i)
        return None