import unicodedata

class Filters:

     def remove_accents(self, text: str) -> str:
        if not text:
            return ""
        
        normalized_text = unicodedata.normalize('NFD', text)
        text_without_accents = "".join([c for c in normalized_text if not unicodedata.combining(c)])

        return text_without_accents
     
     def extract_adress(self, airesponse) -> str:
        adress = f"{airesponse.get('street')}, {airesponse.get('city') + ', ' if airesponse.get('city') else ''}{airesponse.get('state')}"

        return adress
     
     def is_relevant_url(self, url: str) -> bool:
        keywords = ["roubo", "carga", "transporte", "frete", "transportadora", "caminhao", "carreta", "caminhoes", "rodovia", "estrada", "caminh-o", "furtado", "furto", "caminh-es"]
        return any(k in url.lower() for k in keywords)
     
     def is_valid_text(self, text: str) -> bool:
        return text and len(text) > 300