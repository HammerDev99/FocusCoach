# FocusCoach DISC

Coach de IA personalizado con metodologia DISC para desarrollo personal y profesional.

## Descripcion

FocusCoach DISC es un asistente de coaching basado en la metodologia DISC que ayuda a las personas a:

- Comprender su perfil de personalidad DISC (Dominante, Influyente, Sereno, Concienzudo)
- Recibir estrategias de productividad adaptadas a su tipo de personalidad
- Mejorar su comunicacion con personas de otros perfiles
- Gestionar ideas con el sistema Parking Lot para mantener el foco
- Completar proyectos usando el Framework FOCUS-SPRINT

## Stack Tecnologico

- **Frontend**: Streamlit
- **AI**: OpenAI Responses API
- **OCR**: Mistral AI OCR
- **Deployment**: Streamlit Cloud

## Configuracion Local

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar secrets en `.streamlit/secrets.toml`
6. Ejecutar: `streamlit run app.py`

## Configuracion de Secrets

Crear archivo `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-..."
VECTOR_STORE_ID = "vs_..."  # Opcional: base de conocimiento (file_search)
MISTRAL_API_KEY = "..."  # Opcional, para OCR
ANALYTICS_SCRIPT = '<script ...>'  # Opcional
```

## Desarrollado por

**Daniel Arbelaez** - AI Coach Developer

- [GitHub](https://github.com/HammerDev99)
- [LinkedIn](https://www.linkedin.com/in/daniel-arbelaez-/)
- [Website](http://portfolio.sprintjudicial.com/)
