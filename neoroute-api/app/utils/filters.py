import unicodedata

class Filters:

     def remove_acentos(self, texto):
        """entrada: 'texto' -> 'string', saída: 'string' normalizada sem acentos."""
        if not texto:
            return ""
        # Normaliza para NFD (separa caracteres + acentos)
        nfkd = unicodedata.normalize('NFD', texto)
        # Remove caracteres não-ASCII (acentos)
        return "".join([c for c in nfkd if not unicodedata.combining(c)])
     
     def extract_adress(self, airesponse):
        adress = f"{airesponse.street}, {airesponse.city + ', ' if airesponse.city else ''}{airesponse.state}"

        return adress # Retorno em string
     
     def is_relevant_url(self, url: str) -> bool:
        keywords = ["roubo", "carga", "transporte", "frete", "transportadora", "caminhao", "carreta", "caminhoes", "rodovia", "estrada"]
        return any(k in url.lower() for k in keywords)
     
     def is_valid_text(self, texto: str) -> bool:
        return texto and len(texto) > 300