import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    """
    Extrae todo el texto de un archivo PDF de manera limpia.
    
    Args:
        pdf_path (str): Ruta al archivo PDF.
        
    Returns:
        str: Texto extraído del PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No se encontr el archivo: {pdf_path}")

    text = ""
    try:
        # Abrir el documento PDF
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Extraemos el texto de la pgina
            text += page.get_text("text") + "\n"
            
        doc.close()
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        return ""
        
    return text.strip()

if __name__ == "__main__":
    # Test bsico si se ejecuta el script directamente
    # test_path = "ruta/a/tu/archivo.pdf"
    # print(extract_text_from_pdf(test_path))
    pass
