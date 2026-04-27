import re

class TextManager:
    """
    Clase encargada de limpiar y segmentar el texto para una mejor lectura TTS.
    """
    
    @staticmethod
    def clean_text(text):
        """
        Limpia el texto de saltos de lnea innecesarios, guiones de divisin de palabras y espacios extra.
        Tambin corrige palabras fragmentadas por el extractor de PDF (ej: "q ue" -> "que").
        """
        # 1. Quitar guiones de final de lnea (ej: "excep- \n cional" -> "excepcional")
        text = re.sub(r'-\s*\n\s*', '', text)
        
        # 2. Reemplazar saltos de lnea simples por espacios (unir frases cortadas)
        # pero mantenemos los saltos dobles para prrafos.
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        # 3. Corregir palabras fragmentadas comunes (Heurstica avanzada)
        # Lista de palabras comunes en espaol que suelen romperse en PDFs
        palabras_comunes = [
            "que", "para", "entre", "esta", "estas", "este", "estos", "con", "como", 
            "pero", "todo", "toda", "figura", "medio", "donde", "cuando", "forma",
            "desde", "hacia", "sobre", "entre", "mismo", "misma", "sistema", "archivos"
        ]
        
        for word in palabras_comunes:
            # Caso: "q ue" (primera letra separada)
            pattern1 = fr'\b{word[0]}\s+{word[1:]}\b'
            text = re.sub(pattern1, word, text, flags=re.IGNORECASE)
            
            # Caso: "qu e" (ltima letra separada)
            pattern2 = fr'\b{word[:-1]}\s+{word[-1]}\b'
            text = re.sub(pattern2, word, text, flags=re.IGNORECASE)
            
            # Caso: "p a r a" (letras explotadas - solo para palabras cortas)
            if len(word) <= 5:
                exploded = r"\s+".join(list(word))
                text = re.sub(fr'\b{exploded}\b', word, text, flags=re.IGNORECASE)

        # Correcciones especficas de la imagen (ej: "m  s", "f or ma")
        text = re.sub(r'\b(m|M)\s+(á|Á)\s+(s|S)\b', r'\1\2\3', text)
        text = re.sub(r'\b(f|F)\s+or\s+ma\b', r'\1orma', text)
        text = re.sub(r'\b(a|A)\s+bstracción\b', r'\1bstracción', text)
        text = re.sub(r'\b(a|A)\s+rchivo\b', r'\1rchivo', text)
        
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
        Divide el texto en fragmentos que no excedan max_chars,
        respetando el final de los prrafos si es posible.
        Retorna una lista de dicts: [{'text': str, 'start': int, 'end': int}, ...]
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_index = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                current_index += 2 # Por los '\n\n'
                continue
                
            # Si el prrafo es muy largo, lo dividimos por frases
            if len(p) > max_chars:
                sentences = re.split(r'(?<=[.!?]) +', p)
                current_chunk = ""
                chunk_start = current_index
                
                for s in sentences:
                    if len(current_chunk) + len(s) < max_chars:
                        current_chunk += s + " "
                    else:
                        if current_chunk:
                            chunks.append({
                                'text': current_chunk.strip(),
                                'start': chunk_start,
                                'end': chunk_start + len(current_chunk)
                            })
                        current_chunk = s + " "
                        chunk_start = text.find(s, chunk_start)
                
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'start': chunk_start,
                        'end': chunk_start + len(current_chunk)
                    })
            else:
                start_pos = text.find(p, current_index)
                chunks.append({
                    'text': p,
                    'start': start_pos,
                    'end': start_pos + len(p)
                })
                current_index = start_pos + len(p)
                
        return chunks

if __name__ == "__main__":
    sample = "Hola esto es un\ntesto de prueba.\n\nSegunda parte del texto."
    cleaned = TextManager.clean_text(sample)
    print(f"Limpio: {cleaned}")
    print(f"Chunks: {TextManager.get_chunks(cleaned)}")
