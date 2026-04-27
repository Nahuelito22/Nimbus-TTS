from google import genai
import openai
import threading

class AIManager:
    """
    Gestiona la generación de resúmenes utilizando diferentes proveedores de IA.
    Implementa lógica de fallback (si uno falla, intenta con el siguiente).
    """
    def __init__(self, config_manager):
        self.config = config_manager
        
    def summarize(self, text):
        """
        Intenta resumir el texto usando los proveedores configurados.
        Retorna (resumen, modelo_usado) o (None, None) si falla todo.
        """
        primary = self.config.get("preferred_ai_provider")
        providers = ["Gemini", "OpenAI"]
        
        # Reordenar para que el primario vaya primero
        if primary in providers:
            providers.remove(primary)
            providers.insert(0, primary)
            
        for provider in providers:
            resumen, modelo = self._call_provider(provider, text)
            if resumen:
                return resumen, modelo
        
        return None, None

    def _call_provider(self, provider, text):
        """Llama a un proveedor específico."""
        try:
            if provider == "Gemini":
                key = self.config.get("gemini_api_key")
                if not key: return None, None
                
                client = genai.Client(api_key=key)
                prompt = f"Resume el siguiente texto de forma concisa pero completa, usando puntos clave (bullet points) en español:\n\n{text}"
                
                # Lista extendida de modelos candidatos (en orden de preferencia)
                model_candidates = [
                    'gemini-2.0-flash', 
                    'gemini-1.5-flash', 
                    'gemini-1.5-flash-8b',
                    'gemini-1.5-pro'
                ]
                
                last_error = None
                for model_id in model_candidates:
                    try:
                        response = client.models.generate_content(
                            model=model_id,
                            contents=prompt
                        )
                        return response.text, f"Google Gemini ({model_id})"
                    except Exception as e:
                        last_error = str(e)
                        if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                            print(f"Cuota agotada para {model_id}, intentando siguiente...")
                        elif "404" in last_error or "not found" in last_error.lower():
                            print(f"Modelo {model_id} no disponible en esta región/cuenta, intentando siguiente...")
                        else:
                            print(f"Error con {model_id}: {last_error}")
                        continue
                
                print(f"Todos los modelos de Gemini fallaron. Último error: {last_error}")
                
            elif provider == "OpenAI":
                key = self.config.get("openai_api_key")
                if not key: return None, None
                
                client = openai.OpenAI(api_key=key)
                prompt = f"Resume el siguiente texto de forma concisa pero completa, usando puntos clave (bullet points) en español:\n\n{text}"
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content, "OpenAI (GPT-4o mini)"
                
        except Exception as e:
            print(f"Error crítico con proveedor {provider}: {e}")
            
        return None, None
