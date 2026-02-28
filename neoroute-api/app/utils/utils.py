import unicodedata

class Utils:

    def remove_acentos(self, texto):
        """entrada: 'texto' -> 'string', saída: 'string' normalizada sem acentos."""
        if not texto:
            return ""
        # Normaliza para NFD (separa caracteres + acentos)
        nfkd = unicodedata.normalize('NFD', texto)
        # Remove caracteres não-ASCII (acentos)
        return "".join([c for c in nfkd if not unicodedata.combining(c)])
    
    def extract_adress(json):
        """recebe um json e retorna uma string."""
        adress = f"{json['street']}, {json['city'] + ', 'if json['city'] else ''}{json['state']}"

        return adress # Retorno em string