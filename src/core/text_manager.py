import re

class TextManager:
    """
    Clase encargada de limpiar y segmentar el texto para una mejor lectura TTS.
    """
    
    @staticmethod
    def clean_text(text):
        """
        Limpia el texto de saltos de lnea innecesarios, guiones de divisin de palabras y espacios extra.
        """
        # 1. Quitar guiones de final de lnea (ej: "excep- \n cional" -> "excepcional")
        text = re.sub(r'-\s*\n\s*', '', text)
        
        # 2. Reemplazar saltos de lnea simples por espacios (unir frases cortadas)
        # pero mantenemos los saltos dobles para prrafos.
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # 3. Corregir palabras comunes que suelen quedar mal separadas en PDFs (heurstica simple)
        # Unimos letras sueltas que forman palabras comunes
        text = re.sub(r'\b(q|Q)\s+(u|U)\s+(e|E)\b', r'\1\2\3', text)
        text = re.sub(r'\b(l|L)\s+(a|A)\s+(s|S)\b', r'\1\2\3', text)
        text = re.sub(r'\b(l|L)\s+(o|O)\s+(s|S)\b', r'\1\2\3', text)
        text = re.sub(r'\b(c|C)\s+(o|O)\s+(n|N)\b', r'\1\2\3', text)
        
        # 4. Eliminar mltiples espacios en blanco
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    @staticmethod
    def get_paragraphs(text):
        """
        Divide el texto en una lista de prrafos basados en saltos de lnea dobles.
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs

    @staticmethod
    def get_chunks(text, max_chars=1000):
        """
        Opcional: Divide el texto en fragmentos de longitud mxima para procesamiento.
        """
        # Por ahora podemos usar los prrafos como chunks naturales
        paragraphs = TextManager.get_paragraphs(text)
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            if len(current_chunk) + len(p) < max_chars:
                current_chunk += p + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

if __name__ == "__main__":
    sample = "Hola esto es un\ntesto de prueba.\n\nSegunda parte del texto."
    cleaned = TextManager.clean_text(sample)
    print(f"Limpio: {cleaned}")
    print(f"Chunks: {TextManager.get_chunks(cleaned)}")
