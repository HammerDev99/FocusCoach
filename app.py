import os
import streamlit as st
import time
import base64
import json
import requests
import tempfile
import logging
import traceback
import io
import sys
import re
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from openai import OpenAI
import uuid
import streamlit.components.v1 as components

# =============================================
# APPLICATION IDENTITY DICTIONARY
# =============================================
# Todos los elementos especificos de identidad del proyecto estan centralizados aqui
# Modifique este diccionario para cambiar la identidad de la aplicacion

APP_IDENTITY = {
    # Identidad principal
    "name": "FocusCoach DISC",
    "version": "1.0.0",
    "icon": "\U0001f3af",
    "tagline": "Coach de IA Personalizado con Metodologia DISC",
    "full_title": "FocusCoach DISC \U0001f3af",
    # Informacion del desarrollador
    "developer": "Daniel Arbelaez",
    "github_url": "https://github.com/HammerDev99",
    "website_url": "http://portfolio.sprintjudicial.com/",
    "blog_url": "https://blog.sprintjudicial.com/",
    "docs_url": "https://github.com/HammerDev99/FocusCoachDisc/blob/main/README.md",
    "linkedin_url": "https://www.linkedin.com/in/daniel-arbelaez-/",
    "instagram_url": "https://www.instagram.com/daniel_arbe99/",
    "twitter_url": "https://x.com/hammerdev99",
    "youtube_url": "http://youtube.com/@daainti/videos",
    "email": "arbe.94@hotmail.com",
    "repository_url": "https://github.com/HammerDev99/FocusCoachDisc",
    # Descripcion de la aplicacion - formas corta y larga
    "short_description": "Asistente de coaching personalizado basado en la metodologia DISC para desarrollo personal y profesional.",
    "long_description": """
    ### \U0001f3af Hola! Soy FocusCoach DISC

    Estoy aqui para ayudarte a **comprender tu perfil de personalidad DISC** y potenciar tu desarrollo personal y profesional. Utilizo la ciencia de la personalidad como fundamento para personalizar mis intervenciones de coaching.

    #### En que puedo ayudarte?

    * **Analisis de Perfil DISC**: Comprender tus fortalezas, puntos ciegos y estilo de comunicacion segun tu perfil (D, I, S, C)
    * **Productividad Personalizada**: Estrategias de productividad adaptadas a tu tipo de personalidad con el Framework FOCUS-SPRINT
    * **Mejora de Relacionamiento**: Como comunicarte mejor con personas de otros perfiles DISC
    * **Gestion de Ideas (Parking Lot)**: Capturar y organizar tus ideas sin perder el foco en tu proyecto principal
    * **Desarrollo Profesional**: Estrategias de liderazgo, networking y carrera adaptadas a tu perfil
    * **Coaching de Equipos**: Entender la dinamica de tu equipo segun los perfiles DISC

    **Consulta cualquier aspecto sobre personalidad DISC y productividad!**

    *Recuerda: Soy un coach de productividad y desarrollo personal basado en DISC. No soy psicologo ni terapeuta. Para situaciones que requieran atencion profesional, consulta con un especialista.*
    """,
    # User instructions
    "usage_instructions": """
    1. **Analisis de Perfil DISC**: Pregunta sobre cualquiera de los 4 perfiles (Dominante, Influyente, Sereno, Concienzudo) y sus caracteristicas.

    2. **Coaching Personalizado**: Comparte tu perfil DISC (ej: D:75, I:91, S:20, C:76) para recibir recomendaciones adaptadas.

    3. **Productividad**: Solicita estrategias de productividad, sprints de trabajo o gestion de ideas adaptadas a tu perfil.

    4. **Relacionamiento**: Consulta como mejorar tu comunicacion con personas de perfiles diferentes al tuyo.

    5. **Analisis de Documentos**: Carga cartillas DISC, materiales del diplomado o documentos para analisis contextual.
    """,
    # Document processing information
    "document_processing_info": """
    Esta aplicacion utiliza tecnologia de procesamiento de texto para:

    - Analizar cartillas y materiales sobre metodologia DISC
    - Extraer informacion de documentos sobre perfiles de personalidad
    - Procesar graficas de equipos y arquetipos DISC
    - Orientar sobre el contenido de los materiales del diplomado

    **Nota sobre privacidad**: Los documentos se procesan localmente y no se almacenan permanentemente.

    **Formatos soportados**: PDF (.pdf), Texto (.txt), Imagenes (.jpg, .jpeg, .png). Otros formatos no seran procesados.
    """,
    # Texto de la interfaz de usuario
    "chat_placeholder": "Que aspecto de tu perfil DISC quieres explorar hoy?",
    "file_upload_default_message": "He cargado el documento '{files}' para analisis. Por favor, analiza su contenido desde la perspectiva de la metodologia DISC y coaching personalizado.",
    "badges": """
    ![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Ffocuscoachdisc.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)
    """,
    # Welcome message (displayed on first load)
    "welcome_message": """
    ### \U0001f3af Bienvenido a FocusCoach DISC!

    Soy tu coach de IA especializado en **desarrollo personal y profesional basado en la metodologia DISC**. Te ayudo a comprender tu perfil de personalidad, potenciar tus fortalezas y superar tus puntos ciegos.

    **Que puedo hacer por ti:**

    * Ayudarte a entender tu perfil DISC (Dominante, Influyente, Sereno, Concienzudo)
    * Darte estrategias de productividad adaptadas a tu personalidad (Framework FOCUS-SPRINT)
    * Orientarte sobre como mejorar tu comunicacion con otros perfiles
    * Gestionar tus ideas con el sistema Parking Lot para mantener el foco
    * Crear planes de accion personalizados para tus metas profesionales
    * Analizar documentos y cartillas DISC para orientacion contextual

    **Para empezar, te invito a compartir tu perfil DISC si lo conoces, o puedo hacerte algunas preguntas para orientarte!**
    """,
    # Mensajes de error y configuracion
    "api_key_missing": "Por favor, proporciona una clave API para continuar.",
    "assistant_id_missing": "Por favor, proporciona el ID del asistente de OpenAI.",
    "thread_created": "ID del hilo: ",
    "response_error": "No se pudo obtener respuesta. Por favor, intente de nuevo.",
    "config_success": "Configuracion completa",
    "config_warning": "Falta configurar: {missing_items}",
    "config_needed": "**Configuracion incompleta**: {app_name} necesita que configures las claves API y el ID del asistente en el archivo `.streamlit/secrets.toml` o como variables de entorno.",
    # Configuracion del menu
    "menu_items": {
        "Get Help": "https://github.com/HammerDev99/FocusCoachDisc",
        "Report a bug": None,
        "About": "FocusCoach DISC: Coach de IA personalizado con metodologia DISC para desarrollo personal y profesional",
    },
    # Footer text
    "footer_text": """
    **{developer}** - AI Coach Developer

    [GitHub]({github_url}) | [Website]({website_url}) | [Blog]({blog_url}) | [LinkedIn]({linkedin_url}) | [Instagram]({instagram_url}) | [Twitter]({twitter_url}) | [YouTube]({youtube_url}) | [Email](mailto:{email})
    """,
    # Log configuration
    "log_name": "focuscoach",
    # Document naming (for exports and files)
    "document_prefix": "focuscoach",
    "conversation_export_name": "focuscoach_conversacion",
    # Mensajes sobre formatos de archivo
    "allowed_formats_message": "Formatos permitidos: PDF (.pdf), Texto (.txt), Imagenes (.jpg, .jpeg, .png)",
}

# Configuracion avanzada de logging - Implementacion multi-destino
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(
    log_dir, f"{APP_IDENTITY['log_name']}_{datetime.now().strftime('%Y%m%d')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - "
    + APP_IDENTITY["log_name"]
    + " - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
)

# Version de la aplicacion
APP_VERSION = APP_IDENTITY["version"]


# Funcion para inyectar analytics desde secrets
def inject_analytics():
    """Inyecta el script de analytics accediendo al parent document"""
    try:
        if hasattr(st, "secrets") and "ANALYTICS_SCRIPT" in st.secrets:
            # Extraer el website-id del secret para hacerlo generico
            website_id_match = re.search(r'data-website-id="([^"]+)"', st.secrets.ANALYTICS_SCRIPT)
            website_id = website_id_match.group(1) if website_id_match else ""

            script = f"""
            <script>
                // Verificar si el script ya existe para evitar duplicados
                if (!parent.document.querySelector('script[data-website-id="{website_id}"]')) {{
                    var script = parent.document.createElement('script');
                    script.defer = true;
                    script.src = 'https://analytics.sprintjudicial.com/script.js';
                    script.setAttribute('data-website-id', '{website_id}');
                    parent.document.head.appendChild(script);
                }}
            </script>
            """
            components.html(script, height=0)
    except Exception:
        # Analytics is optional, silently skip if secrets are not configured
        pass


# Configuracion de pagina Streamlit
st.set_page_config(
    page_title=APP_IDENTITY["full_title"],
    page_icon=APP_IDENTITY["icon"],
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=APP_IDENTITY["menu_items"],
)

# Inyectar analytics de Umami
inject_analytics()


# Decorador para manejo de errores con retries
def handle_error(max_retries=2):
    """
    Decorador avanzado para manejo de errores con capacidad de reintento
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = f"Error en {func.__name__} (intento {retries+1}/{max_retries+1}): {str(e)}"
                    logging.error(error_msg)

                    if retries < max_retries:
                        logging.info(f"Reintentando {func.__name__}...")
                        retries += 1
                        time.sleep(1)
                    else:
                        logging.error(
                            f"Error final despues de {max_retries+1} intentos: {traceback.format_exc()}"
                        )
                        st.error(error_msg)
                        break

            return None

        return wrapper

    return decorator


# Sistema de feedback del usuario
@st.dialog("Tu opinion nos importa", width="large")
def show_feedback_dialog():
    """
    Muestra un dialogo solicitando feedback del usuario con enlace a formulario externo.
    """
    st.markdown("""
    ### Ayudanos a mejorar FocusCoach DISC! Tu experiencia es valiosa para nosotros. Nos gustaria conocer tu opinion.

    **La encuesta toma solo 2 minutos.**
    """)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        feedback_url = st.secrets.get("FEEDBACK_URL", "https://forms.office.com/r/p9X57fsnF5")
        st.link_button(
            "Responder encuesta",
            feedback_url,
            use_container_width=True,
            type="primary"
        )

    with col2:
        if st.button("Recordar mas tarde", use_container_width=True):
            st.session_state.feedback_reminded = True
            st.rerun()

    with col3:
        if st.button("X", use_container_width=True, type="secondary", help="No volver a mostrar"):
            st.session_state.feedback_dismissed = True
            st.rerun()


# Sistema multicapa para reinicio de la aplicacion
def rerun_app():
    """
    Sistema multicapa para reiniciar la aplicacion Streamlit.
    """
    try:
        st.rerun()
    except (AttributeError, Exception) as e:
        logging.warning(f"Metodo primario de reinicio fallo: {str(e)}")
        st.info("Por favor, recarga la pagina para ver los cambios")
        try:
            html_code = """
            <script>
                setTimeout(function() {
                    window.parent.location.reload();
                }, 2000);
            </script>
            """
            st.components.v1.html(html_code, height=0, width=0)
        except Exception as e3:
            logging.error(f"Reinicio con JavaScript fallo: {str(e3)}")


# Detectar entorno de ejecucion
def is_streamlit_cloud():
    """
    Detecta si la aplicacion se esta ejecutando en Streamlit Cloud
    """
    try:
        indicators = [
            os.environ.get("STREAMLIT_SHARING_MODE") is not None,
            os.environ.get("STREAMLIT_SERVER_BASE_URL_IS_SET") is not None,
            os.environ.get("IS_STREAMLIT_CLOUD") == "true",
            os.path.exists("/.streamlit/config.toml"),
            "STREAMLIT_RUNTIME" in os.environ,
        ]
        return sum(indicators) >= 2
    except Exception as e:
        logging.warning(f"Error al detectar entorno: {str(e)}")
        return False


# Crear cliente OpenAI para Assistants
@handle_error(max_retries=1)
def create_openai_client(api_key):
    """
    Crea un cliente OpenAI con encabezados compatibles con Assistants API v2
    """
    try:
        client = OpenAI(
            api_key=api_key, default_headers={"OpenAI-Beta": "assistants=v2"}
        )
        models = client.models.list()
        if not models:
            raise Exception("No se pudo obtener la lista de modelos")
        logging.info("Cliente OpenAI inicializado correctamente")
        return client
    except Exception as e:
        logging.error(f"Error inicializando cliente OpenAI: {str(e)}")
        st.error(f"No se pudo conectar a OpenAI: {str(e)}")
        return None


# Sistema multicapa para exportacion de conversaciones
def export_chat_to_pdf(messages):
    """
    Sistema multicapa para exportacion de conversaciones a PDF.
    """
    try:
        return _export_chat_to_pdf_primary(messages)
    except Exception as e:
        logging.warning(f"Metodo primario de exportacion a PDF fallo: {str(e)}")
        try:
            return _export_chat_to_pdf_secondary(messages)
        except Exception as e2:
            logging.warning(f"Metodo secundario de exportacion a PDF fallo: {str(e2)}")
            try:
                return _export_chat_to_pdf_fallback(messages)
            except Exception as e3:
                logging.error(f"Todos los metodos de exportacion a PDF fallaron: {str(e3)}")
                md_content = export_chat_to_markdown(messages)
                st.warning("No fue posible generar un PDF. Se ha creado un archivo markdown en su lugar.")
                return base64.b64encode(md_content.encode()).decode(), "markdown"


def _export_chat_to_pdf_primary(messages):
    """Metodo primario: FPDF optimizado"""
    from fpdf import FPDF

    class CustomPDF(FPDF):
        def header(self):
            self.set_font("helvetica", "B", 12)
            self.cell(0, 10, f'{APP_IDENTITY["name"]} - Historial de Conversacion', 0, new_y="NEXT", align="C")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

        def add_message(self, role, content):
            self.set_font("helvetica", "B", 11)
            self.cell(0, 10, role, 0, new_y="NEXT", align="L")
            self.ln(2)
            self.set_font("helvetica", "", 10)
            self._safe_add_content(content)
            self.ln(5)

        def _safe_add_content(self, content):
            content = re.sub(r"^#{1,6}\s+(.*?)$", r"\1", content, flags=re.MULTILINE)
            content = re.sub(r"!\[.*?\]\(.*?\)", "[IMAGEN]", content)
            content = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", content)
            paragraphs = content.split("\n\n")
            for paragraph in paragraphs:
                if not paragraph.strip():
                    self.ln(5)
                    continue
                lines = paragraph.split("\n")
                for line in lines:
                    if not line.strip():
                        continue
                    safe_txt = "".join(c if ord(c) < 128 else "?" for c in line)
                    try:
                        self.multi_cell(0, 10, safe_txt)
                    except Exception:
                        pass
                self.ln(2)

    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, new_y="NEXT")
    pdf.ln(5)

    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        pdf.add_message(role, msg["content"])

    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue(), "pdf"


def _export_chat_to_pdf_secondary(messages):
    """Metodo secundario: ReportLab"""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="DocTitle", fontName="Helvetica-Bold", fontSize=14, alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name="User", fontName="Helvetica-Bold", fontSize=12, textColor=colors.blue, spaceAfter=6))
    styles.add(ParagraphStyle(name="Assistant", fontName="Helvetica-Bold", fontSize=12, textColor=colors.green, spaceAfter=6))

    elements = []
    elements.append(Paragraph(f"{APP_IDENTITY['name']} - Historial de Conversacion", styles["DocTitle"]))
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Italic"]))
    elements.append(Spacer(1, 0.25 * inch))

    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        style = styles["User"] if msg["role"] == "user" else styles["Assistant"]
        elements.append(Paragraph(role, style))
        safe_text = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
        try:
            elements.append(Paragraph(safe_text[:3000], styles["Normal"]))
        except Exception:
            elements.append(Paragraph("[Contenido simplificado]", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data, "pdf"


def _export_chat_to_pdf_fallback(messages):
    """Metodo de ultimo recurso: PDF simple"""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(200, 10, f"{APP_IDENTITY['name']} - Historial de Conversacion", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("helvetica", style="I", size=10)
    pdf.cell(200, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    pdf.set_font("helvetica", size=11)

    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(200, 10, role, ln=True)
        pdf.ln(2)
        pdf.set_font("helvetica", size=10)
        simple_text = "".join(c if ord(c) < 128 else "?" for c in msg["content"])
        simple_text = simple_text.replace("\n", " ").replace("\r", "")
        for i in range(0, len(simple_text), 80):
            chunk = simple_text[i : i + 80]
            try:
                pdf.cell(0, 10, chunk, ln=True)
            except Exception:
                pass
        pdf.ln(10)

    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue(), "pdf"


def export_chat_to_markdown(messages):
    """Exporta el historial de chat a formato markdown"""
    md_content = f"# {APP_IDENTITY['name']} - Historial de Conversacion\n\n"
    md_content += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        md_content += f"## {role}\n\n{msg['content']}\n\n"
        md_content += "---\n\n"

    return md_content


# Definicion de formatos permitidos
ALLOWED_FILE_FORMATS = {
    "PDF": [".pdf"],
    "Imagen": [".jpg", ".jpeg", ".png"],
    "Texto": [".txt"],
}

ALLOWED_EXTENSIONS = [ext for exts in ALLOWED_FILE_FORMATS.values() for ext in exts]


# Funciones de OCR con Mistral
@handle_error(max_retries=1)
def validate_file_format(file):
    """Valida que el archivo tenga un formato permitido"""
    file_type = None

    if not hasattr(file, "name"):
        return False, None, "El archivo no tiene nombre"

    file_name = file.name.lower()
    file_ext = os.path.splitext(file_name)[1]

    if file_ext not in ALLOWED_EXTENSIONS:
        allowed_exts = ", ".join(ALLOWED_EXTENSIONS)
        return False, None, f"Formato de archivo no permitido. Use: {allowed_exts}"

    for doc_type, extensions in ALLOWED_FILE_FORMATS.items():
        if file_ext in extensions:
            file_type = doc_type
            break

    try:
        position = file.tell()
        if file_type == "PDF":
            header = file.read(8)
            file.seek(position)
            if not header.startswith(b"%PDF"):
                return False, None, "El archivo no es un PDF valido"
        elif file_type == "Imagen":
            try:
                img = Image.open(file)
                img.verify()
                file.seek(position)
            except Exception as e:
                file.seek(position)
                return False, None, f"El archivo no es una imagen valida: {str(e)}"
    except Exception as e:
        try:
            file.seek(position)
        except Exception:
            pass
        return False, None, f"Error validando el archivo: {str(e)}"

    return True, file_type, None


@handle_error(max_retries=1)
def prepare_image_for_ocr(file_data):
    """Prepara una imagen para ser procesada con OCR"""
    try:
        img = Image.open(BytesIO(file_data))

        if img.mode != "L" and img.mode != "1":
            img = img.convert("L")

        max_dimension = 4000
        if img.width > max_dimension or img.height > max_dimension:
            ratio = min(max_dimension / img.width, max_dimension / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        save_format = "JPEG"
        histogram = img.histogram()
        if img.mode == "L" and (histogram[0] + histogram[-1]) > sum(histogram) * 0.8:
            save_format = "PNG"

        buffer = BytesIO()
        if save_format == "JPEG":
            img.save(buffer, format=save_format, quality=95, optimize=True)
        else:
            img.save(buffer, format=save_format, optimize=True)

        buffer.seek(0)
        return buffer.read(), f"image/{save_format.lower()}"
    except Exception as e:
        logging.warning(f"Optimizacion de imagen fallida: {str(e)}")
        return file_data, "image/jpeg"


@handle_error(max_retries=1)
def extract_text_from_ocr_response(response):
    """Extrae texto de diferentes formatos de respuesta OCR"""
    logging.info(f"Procesando respuesta OCR de tipo: {type(response)}")

    if "pages" in response and isinstance(response["pages"], list):
        pages = response["pages"]
        if pages and "markdown" in pages[0]:
            markdown_text = "\n\n".join(page.get("markdown", "") for page in pages)
            if markdown_text.strip():
                return {"text": markdown_text, "format": "markdown"}

    if "text" in response:
        return {"text": response["text"], "format": "text"}

    if "elements" in response:
        elements = response["elements"]
        if isinstance(elements, list):
            text_parts = []
            for element in elements:
                if "text" in element:
                    text_parts.append(element["text"])
            return {"text": "\n".join(text_parts), "format": "elements"}

    if "content" in response:
        return {"text": response["content"], "format": "content"}

    try:
        response_str = json.dumps(response, indent=2)
        if len(response_str) > 10000:
            response_str = response_str[:10000] + "... [truncado]"

        extracted_text = extract_all_text_fields(response)
        if extracted_text:
            return {"text": extracted_text, "format": "extracted"}

        return {
            "text": "No se pudo encontrar texto estructurado en la respuesta OCR.",
            "format": "unknown",
            "raw_response": response_str,
        }
    except Exception as e:
        logging.error(f"Error al procesar respuesta OCR: {str(e)}")
        return {"error": f"Error al procesar la respuesta: {str(e)}"}


@handle_error(max_retries=0)
def extract_all_text_fields(data, prefix="", max_depth=5, current_depth=0):
    """Funcion recursiva para extraer todos los campos de texto"""
    if current_depth > max_depth:
        return []

    result = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, str) and len(value) > 1:
                result.append(f"{new_prefix}: {value}")
            elif isinstance(value, (dict, list)) and value:
                child_results = extract_all_text_fields(value, new_prefix, max_depth, current_depth + 1)
                result.extend(child_results)

    elif isinstance(data, list):
        max_items = 20
        for i, item in enumerate(data[:max_items]):
            new_prefix = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)) and item:
                child_results = extract_all_text_fields(item, new_prefix, max_depth, current_depth + 1)
                result.extend(child_results)
            elif isinstance(item, str) and len(item) > 1:
                result.append(f"{new_prefix}: {item}")

        if len(data) > max_items:
            result.append(f"{prefix}: [... {len(data) - max_items} elementos adicionales omitidos]")

    return "\n".join(result)


@handle_error(max_retries=1)
def process_document_with_mistral_ocr(api_key, file_bytes, file_type, file_name):
    """Procesa un documento con OCR de Mistral"""
    job_id = str(uuid.uuid4())
    logging.info(f"Procesando documento {file_name} con Mistral OCR (ID: {job_id})")

    with st.status(f"Procesando documento {file_name}...", expanded=True) as status:
        try:
            status.update(label="Preparando documento para OCR...", state="running")

            debug_dir = os.path.join(tempfile.gettempdir(), f"{APP_IDENTITY['document_prefix']}_debug")
            os.makedirs(debug_dir, exist_ok=True)
            debug_file_path = os.path.join(debug_dir, f"debug_{job_id}_{file_name}")

            with open(debug_file_path, "wb") as f:
                f.write(file_bytes)

            if file_type == "PDF":
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                    page_count = len(reader.pages)
                    logging.info(f"PDF valido con {page_count} paginas")
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                    document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_file}"}
                except Exception as e:
                    logging.error(f"Error al validar PDF: {str(e)}")
                    status.update(label=f"Error al validar PDF: {str(e)}", state="error")
                    return {"error": f"El archivo no es un PDF valido: {str(e)}"}

            elif file_type == "Imagen":
                try:
                    optimized_bytes, mime_type = prepare_image_for_ocr(file_bytes)
                    encoded_file = base64.b64encode(optimized_bytes).decode("utf-8")
                    document = {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded_file}"}
                except Exception as e:
                    logging.error(f"Error al procesar imagen: {str(e)}")
                    status.update(label=f"Error al procesar imagen: {str(e)}", state="error")
                    return {"error": f"El archivo no es una imagen valida: {str(e)}"}

            elif file_type == "Texto":
                try:
                    try:
                        text_content = file_bytes.decode("utf-8")
                        return {"text": text_content, "format": "text"}
                    except UnicodeDecodeError:
                        for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                            try:
                                text_content = file_bytes.decode(encoding)
                                return {"text": text_content, "format": "text"}
                            except UnicodeDecodeError:
                                continue
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                    document = {"type": "document_url", "document_url": f"data:text/plain;base64,{encoded_file}"}
                except Exception as e:
                    logging.error(f"Error al procesar documento de texto: {str(e)}")
                    return {"error": f"Error al procesar documento de texto: {str(e)}"}
            else:
                return {"error": f"Tipo de documento no soportado: {file_type}"}

            status.update(label="Enviando documento a la API de Mistral...", state="running")

            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            payload = {"model": "mistral-ocr-latest", "document": document}

            max_retries = 2
            retry_delay = 2

            for retry in range(max_retries + 1):
                try:
                    response = requests.post("https://api.mistral.ai/v1/ocr", json=payload, headers=headers, timeout=90)

                    if response.status_code == 200:
                        result = response.json()
                        status.update(label=f"Documento {file_name} procesado exitosamente", state="complete")
                        extracted_content = extract_text_from_ocr_response(result)
                        if "error" in extracted_content:
                            return {"error": extracted_content["error"], "raw_response": result}
                        return extracted_content
                    elif response.status_code == 429:
                        if retry < max_retries:
                            wait_time = retry_delay * (retry + 1)
                            status.update(label=f"Limite de tasa alcanzado. Reintentando en {wait_time}s...", state="running")
                            time.sleep(wait_time)
                            continue
                        else:
                            return {"error": "Limite de tasa alcanzado despues de reintentos.", "raw_response": response.text}
                    else:
                        error_message = f"Error en API OCR ({response.status_code}): {response.text[:500]}"
                        logging.error(error_message)
                        status.update(label=f"Error: {error_message}", state="error")
                        break
                except requests.exceptions.Timeout:
                    if retry < max_retries:
                        time.sleep(retry_delay * (retry + 1))
                    else:
                        return {"error": "Timeout al contactar API despues de multiples intentos."}
                except Exception as e:
                    if retry < max_retries:
                        time.sleep(retry_delay * (retry + 1))
                    else:
                        return {"error": f"Error al procesar documento: {str(e)}"}

            return {"error": "Error despues de reintentos"}

        except Exception as e:
            error_message = f"Error general al procesar documento: {str(e)}"
            logging.error(error_message)
            return {"error": error_message}


# Funcion para gestionar el contexto de documentos
@handle_error(max_retries=0)
def manage_document_context():
    """Permite al usuario gestionar que documentos mantener en el contexto"""
    if "document_contents" in st.session_state and st.session_state.document_contents:
        st.write("Documentos en contexto actual:")
        docs_to_keep = {}
        for doc_name in st.session_state.document_contents:
            docs_to_keep[doc_name] = st.checkbox(f"{doc_name}", value=True, key=f"keep_{doc_name}")

        if st.button("Actualizar contexto", key="update_context"):
            docs_to_remove = [doc for doc, keep in docs_to_keep.items() if not keep]
            if docs_to_remove:
                for doc in docs_to_remove:
                    if doc in st.session_state.document_contents:
                        del st.session_state.document_contents[doc]
                    if doc in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.remove(doc)
                st.success(f"Se eliminaron {len(docs_to_remove)} documentos del contexto.")
                rerun_app()
            else:
                st.info("No se seleccionaron documentos para eliminar.")
    else:
        st.info("No hay documentos cargados en el contexto actual.")


# Funciones de OpenAI Assistants
@handle_error(max_retries=1)
def initialize_thread(client):
    """Inicializa un nuevo thread de conversacion"""
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        logging.info(f"Thread creado: {thread_id}")
        test_thread = client.beta.threads.retrieve(thread_id=thread_id)
        if not test_thread or not hasattr(test_thread, "id"):
            raise Exception("El thread se creo pero no se puede recuperar")
        return thread_id
    except Exception as e:
        logging.error(f"Error creando thread: {str(e)}")
        st.error("No se pudo inicializar la conversacion con el asistente")
        return None


@handle_error(max_retries=1)
def process_message_with_citations(message):
    """Extrae y formatea el texto del mensaje del asistente con citas"""
    try:
        if not hasattr(message, "content") or not message.content:
            return "No se pudo procesar el mensaje"

        processed_content = ""
        for content_item in message.content:
            if hasattr(content_item, "text") and content_item.text:
                text_value = content_item.text.value
                annotations = []

                if hasattr(content_item.text, "annotations") and content_item.text.annotations:
                    annotations = content_item.text.annotations

                    if annotations:
                        citations = []
                        for idx, annotation in enumerate(annotations):
                            text_value = text_value.replace(annotation.text, f"[{idx+1}]")
                            if file_citation := getattr(annotation, "file_citation", None):
                                file_id = file_citation.file_id
                                file_name = "Documento de referencia"
                                if "file_metadata" in st.session_state and file_id in st.session_state.file_metadata:
                                    file_name = st.session_state.file_metadata[file_id]["name"]
                                citations.append(f"[{idx+1}] Fuente: {file_name}")

                        if citations:
                            text_value += "\n\n--- Referencias: ---\n" + "\n".join(citations)

                processed_content += text_value
            else:
                processed_content += str(content_item)

        return processed_content
    except Exception as e:
        logging.error(f"Error procesando mensaje: {str(e)}")
        return "Error al procesar la respuesta del asistente"


@handle_error(max_retries=1)
def send_message_with_document_context(client, thread_id, assistant_id, prompt, current_doc_contents=None):
    """Envia un mensaje al asistente incluyendo el contexto de documentos"""
    try:
        full_prompt = prompt
        all_doc_contents = {}

        if "document_contents" in st.session_state:
            all_doc_contents.update(st.session_state.document_contents)

        if current_doc_contents and isinstance(current_doc_contents, dict):
            all_doc_contents.update(current_doc_contents)
            if "document_contents" not in st.session_state:
                st.session_state.document_contents = {}
            st.session_state.document_contents.update(current_doc_contents)

        if all_doc_contents and len(all_doc_contents) > 0:
            document_context = "\n\n### Contexto de documentos procesados:\n\n"
            for doc_name, doc_content in all_doc_contents.items():
                if isinstance(doc_content, dict):
                    if "text" in doc_content:
                        doc_text = doc_content["text"][:5000] + "..." if len(doc_content["text"]) > 5000 else doc_content["text"]
                        document_context += f"-- Documento: {doc_name} --\n{doc_text}\n\n"
                    elif "error" in doc_content and "raw_response" in doc_content:
                        raw_response = doc_content["raw_response"]
                        if isinstance(raw_response, dict) and "text" in raw_response:
                            doc_text = raw_response["text"][:5000] + "..." if len(raw_response["text"]) > 5000 else raw_response["text"]
                            document_context += f"-- Documento: {doc_name} --\n{doc_text}\n\n"
                        else:
                            document_context += f"-- Documento: {doc_name} -- (Error al extraer texto: {doc_content['error']})\n\n"
                    else:
                        document_context += f"-- Documento: {doc_name} -- (No se pudo extraer texto)\n\n"

            if len(document_context) > 60:
                full_prompt = f"{prompt}\n\n{document_context}"
                logging.info(f"Prompt enriquecido con contexto de {len(all_doc_contents)} documentos. Tamano total: {len(full_prompt)} caracteres")

        # Crear mensaje
        message = None
        for attempt in range(2):
            try:
                message = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=full_prompt)
                break
            except Exception as e:
                if attempt == 0:
                    logging.warning(f"Error al crear mensaje (intento 1): {str(e)}. Reintentando...")
                    time.sleep(2)
                else:
                    raise Exception(f"Error al crear mensaje: {str(e)}")

        if not message:
            raise Exception("No se pudo crear el mensaje despues de reintentos")

        # Crear ejecucion
        run = None
        for attempt in range(2):
            try:
                run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
                break
            except Exception as e:
                if attempt == 0:
                    logging.warning(f"Error al crear ejecucion (intento 1): {str(e)}. Reintentando...")
                    time.sleep(2)
                else:
                    raise Exception(f"Error al crear ejecucion: {str(e)}")

        if not run:
            raise Exception("No se pudo iniciar la ejecucion despues de reintentos")

        # Esperar completacion
        with st.status("Analizando tu consulta y preparando coaching personalizado...", expanded=True) as status:
            max_run_time = 120
            start_time = time.time()

            while run.status not in ["completed", "failed", "cancelled", "expired"]:
                time.sleep(1)
                elapsed_time = time.time() - start_time
                if elapsed_time > max_run_time:
                    status.update(label="La operacion esta tomando demasiado tiempo. Intente nuevamente.", state="error")
                    return None

                try:
                    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                except Exception:
                    pass

                if run.status == "in_progress":
                    status.update(label="Procesando tu consulta con coaching DISC personalizado...", state="running")
                elif run.status == "requires_action":
                    status.update(label="Realizando acciones requeridas...", state="running")

                if run.status == "failed":
                    status.update(label="Error en el procesamiento", state="error")
                    return None

            if run.status == "completed":
                status.update(label="Coaching completado", state="complete")

        # Recuperar mensajes
        if run.status == "completed":
            try:
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                for message in messages.data:
                    if message.role == "assistant" and not any(
                        msg["role"] == "assistant" and msg.get("id") == message.id
                        for msg in st.session_state.messages
                    ):
                        full_response = process_message_with_citations(message)
                        return {"role": "assistant", "content": full_response, "id": message.id}
                return None
            except Exception as e:
                logging.error(f"Error al recuperar mensajes: {str(e)}")
                return None

        return None
    except Exception as e:
        logging.error(f"Error en comunicacion con OpenAI: {str(e)}")
        st.error("Ocurrio un error al comunicarse con el asistente. Por favor, intente nuevamente.")
        return None


# Funcion para limpiar la sesion actual
@handle_error(max_retries=0)
def clean_current_session():
    """Limpia todos los recursos de la sesion actual"""
    try:
        resources_cleaned = {
            "documents": len(st.session_state.get("document_contents", {})),
            "messages": len(st.session_state.get("messages", [])),
        }

        if "document_contents" in st.session_state:
            st.session_state.document_contents = {}
        if "uploaded_files" in st.session_state:
            st.session_state.uploaded_files = []
        if "messages" in st.session_state:
            st.session_state.messages = []
        for key in ["file_metadata"]:
            if key in st.session_state:
                st.session_state[key] = {}

        logging.info(f"Sesion limpiada: {resources_cleaned['documents']} documentos, {resources_cleaned['messages']} mensajes")
        return resources_cleaned
    except Exception as e:
        logging.error(f"Error limpiando sesion: {str(e)}")
        return {"documents": 0, "messages": 0, "error": str(e)}


# ----- INICIALIZACION DE INTERFAZ -----

# Titulo principal
st.title(f"{APP_IDENTITY['name']} {APP_IDENTITY['icon']} {APP_IDENTITY['tagline']}")

# Barra lateral
with st.sidebar:
    st.title(f"{APP_IDENTITY['icon']} Configuracion y Recursos")

    # Obtener API Key de OpenAI
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
    if not openai_api_key:
        openai_api_key = st.text_input("API Key de OpenAI", type="password", help="Ingrese su API Key de OpenAI")

    # Obtener API Key de Mistral
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    if not mistral_api_key and hasattr(st, "secrets") and "MISTRAL_API_KEY" in st.secrets:
        mistral_api_key = st.secrets["MISTRAL_API_KEY"]
    if not mistral_api_key:
        mistral_api_key = st.text_input("API Key de Mistral", type="password", help="Ingrese su API Key de Mistral para OCR")

    # Obtener Assistant ID
    assistant_id = os.environ.get("ASSISTANT_ID")
    if not assistant_id and hasattr(st, "secrets") and "ASSISTANT_ID" in st.secrets:
        assistant_id = st.secrets["ASSISTANT_ID"]
    if not assistant_id:
        assistant_id = st.text_input("ID del Asistente", type="password", help="Ingrese el ID del asistente de OpenAI")

    # Verificar configuracion
    if openai_api_key and mistral_api_key and assistant_id:
        st.success(APP_IDENTITY["config_success"])
    else:
        missing = []
        if not openai_api_key:
            missing.append("API Key de OpenAI")
        if not mistral_api_key:
            missing.append("API Key de Mistral")
        if not assistant_id:
            missing.append("ID del Asistente")
        st.warning(APP_IDENTITY["config_warning"].format(missing_items=", ".join(missing)))

    env_type = "Streamlit Cloud" if is_streamlit_cloud() else "Local"
    st.info(f"Entorno detectado: {env_type}")

    # Opciones de exportacion
    st.subheader("Exportar Conversacion")
    export_format = st.radio("Formato de exportacion:", ("Markdown",))

    if st.button("Descargar conversacion"):
        if "messages" in st.session_state and st.session_state.messages:
            if export_format == "Markdown":
                md_content = export_chat_to_markdown(st.session_state.messages)
                b64 = base64.b64encode(md_content.encode()).decode()
                href = f'<a href="data:text/markdown;base64,{b64}" download="{APP_IDENTITY["conversation_export_name"]}.md">Descargar archivo Markdown</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("No hay conversacion para exportar.")

    # Administrador de contexto de documentos
    st.subheader("Gestion de Documentos")
    manage_document_context()

    # Boton para limpiar sesion
    if st.button("Limpiar sesion actual", type="secondary", help="Elimina todos los archivos y datos de la sesion actual"):
        with st.spinner("Limpiando recursos de la sesion..."):
            result = clean_current_session()
            if isinstance(result, dict) and "error" not in result:
                st.success(f"Sesion limpiada: {result['documents']} documentos, {result['messages']} mensajes")
            else:
                st.error("No se pudo limpiar la sesion completamente")
            rerun_app()

    # Documentos cargados
    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        st.subheader("Documentos disponibles")
        for idx, filename in enumerate(st.session_state.uploaded_files):
            st.markdown(f"**{filename}**")
        st.info("Estos documentos estan disponibles para consulta en la conversacion.")

    # Recursos DISC
    st.markdown("---")
    st.subheader("Recursos DISC")

    st.markdown("**Perfiles DISC:**")
    st.markdown("- **D (Rojo)**: Dominante - Orientado a resultados")
    st.markdown("- **I (Amarillo)**: Influyente - Orientado a personas")
    st.markdown("- **S (Verde)**: Sereno - Orientado a estabilidad")
    st.markdown("- **C (Azul)**: Concienzudo - Orientado a calidad")

    st.markdown("**Recursos externos:**")
    st.markdown("- [DISC Profile - Wikipedia](https://en.wikipedia.org/wiki/DISC_assessment)")
    st.markdown("- [Framework FOCUS-SPRINT](https://github.com/HammerDev99/FocusCoachDisc)")

    # Area informativa
    st.markdown("---")
    st.subheader(f"{APP_IDENTITY['icon']} Sobre {APP_IDENTITY['name']}")
    st.markdown(APP_IDENTITY["long_description"])

    # Informacion de uso
    st.markdown("---")
    st.subheader("Como usar " + APP_IDENTITY["name"])
    st.markdown(APP_IDENTITY["usage_instructions"])

    # Instrucciones para documentos
    st.markdown("---")
    st.subheader("Procesamiento de documentos")
    st.info(APP_IDENTITY["document_processing_info"])
    st.caption(APP_IDENTITY["allowed_formats_message"])

    # Seccion de feedback
    st.markdown("---")
    st.subheader("Feedback")
    if st.button("Completar encuesta de satisfaccion", use_container_width=True, key="sidebar_feedback_btn"):
        st.session_state.feedback_dialog_shown = False
        show_feedback_dialog()

    # Footer
    st.markdown("---")
    st.subheader("Desarrollado por:")
    st.markdown(
        APP_IDENTITY["footer_text"].format(
            developer=APP_IDENTITY["developer"],
            github_url=APP_IDENTITY["github_url"],
            website_url=APP_IDENTITY["website_url"],
            blog_url=APP_IDENTITY["blog_url"],
            linkedin_url=APP_IDENTITY["linkedin_url"],
            instagram_url=APP_IDENTITY["instagram_url"],
            twitter_url=APP_IDENTITY["twitter_url"],
            youtube_url=APP_IDENTITY["youtube_url"],
            email=APP_IDENTITY["email"],
        ),
        unsafe_allow_html=True,
    )

# Detener si no hay configuracion completa
if not openai_api_key or not mistral_api_key or not assistant_id:
    st.markdown(APP_IDENTITY["config_needed"].format(app_name=APP_IDENTITY["name"]))
    st.stop()

# ----- INICIALIZACION DE ESTADO -----

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "document_contents" not in st.session_state:
    st.session_state.document_contents = {}
if "file_metadata" not in st.session_state:
    st.session_state.file_metadata = {}
if "feedback_toast_shown" not in st.session_state:
    st.session_state.feedback_toast_shown = False
if "feedback_dialog_shown" not in st.session_state:
    st.session_state.feedback_dialog_shown = False
if "feedback_dismissed" not in st.session_state:
    st.session_state.feedback_dismissed = False
if "feedback_reminded" not in st.session_state:
    st.session_state.feedback_reminded = False

# Crear clientes
openai_client = create_openai_client(openai_api_key)

# Inicializar thread
if not st.session_state.thread_id and openai_client:
    with st.spinner("Inicializando coach DISC..."):
        thread_id = initialize_thread(openai_client)
        if thread_id:
            st.session_state.thread_id = thread_id
            st.success(f"{APP_IDENTITY['icon']} Coach DISC inicializado correctamente {APP_IDENTITY['icon']}")

# Mostrar feedback dialog
if (st.session_state.thread_id
    and not st.session_state.feedback_dismissed
    and not st.session_state.feedback_reminded):

    if not st.session_state.feedback_toast_shown:
        st.toast("Tu feedback nos ayuda a mejorar FocusCoach DISC", icon="\U0001f4ac")
        st.session_state.feedback_toast_shown = True

    if not st.session_state.feedback_dialog_shown:
        st.session_state.feedback_dialog_shown = True
        show_feedback_dialog()

# ----- INTERFAZ DE CHAT -----

chat_history_container = st.container()

with chat_history_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(APP_IDENTITY["welcome_message"])

# Chat input con soporte para archivos
file_types = [ext[1:] for ext in ALLOWED_EXTENSIONS]
st.caption(APP_IDENTITY["allowed_formats_message"])

prompt = st.chat_input(
    APP_IDENTITY["chat_placeholder"],
    accept_file=True,
    file_type=file_types,
)

# Procesar entrada del usuario
if prompt:
    user_text = ""
    user_files = []

    if hasattr(prompt, "text"):
        user_text = prompt.text
    if hasattr(prompt, "files") and prompt.files:
        user_files = prompt.files
    elif isinstance(prompt, dict) and "files" in prompt and prompt["files"]:
        user_files = prompt["files"]

    current_doc_contents = {}

    # Procesar archivos con OCR
    if user_files:
        with st.spinner("Procesando documentos con OCR..."):
            valid_files = 0
            invalid_files = 0

            for file in user_files:
                is_valid, file_type, error_message = validate_file_format(file)

                if not is_valid:
                    st.error(f"Error en archivo {file.name}: {error_message}")
                    invalid_files += 1
                    continue

                if file.name not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.append(file.name)

                file_bytes = file.read()
                file.seek(0)

                try:
                    ocr_results = process_document_with_mistral_ocr(mistral_api_key, file_bytes, file_type, file.name)

                    if ocr_results and "error" not in ocr_results:
                        current_doc_contents[file.name] = ocr_results
                        st.session_state.document_contents[file.name] = ocr_results
                        st.success(f"Documento {file.name} procesado correctamente")
                        valid_files += 1
                    else:
                        error_msg = ocr_results.get("error", "Error desconocido")
                        st.warning(f"No se pudo extraer texto completo de {file.name}: {error_msg}")
                        st.session_state.document_contents[file.name] = ocr_results
                except Exception as e:
                    st.error(f"Error procesando {file.name}: {str(e)}")

            if invalid_files > 0:
                st.warning(f"{invalid_files} archivo(s) no valido(s) fueron omitidos. {APP_IDENTITY['allowed_formats_message']}")

                if invalid_files == len(user_files) and len(user_files) > 0:
                    st.error("No se pudo procesar ningun archivo. Verifique que los archivos cumplan con los formatos permitidos.")

    # Generar mensaje automatico si solo hay archivos sin texto
    if not user_text and user_files:
        file_names = [f.name for f in user_files]
        user_text = APP_IDENTITY["file_upload_default_message"].format(files=", ".join(file_names))

    if not user_text and not user_files:
        st.warning("Por favor, ingrese un mensaje o adjunte un archivo para continuar.")
    else:
        display_message = user_text
        if user_files:
            file_names = [f.name for f in user_files]
            if user_text:
                display_message = f"{user_text}\n\n*Archivo adjunto: {', '.join(file_names)}*"
            else:
                display_message = f"*Archivo adjunto para analisis: {', '.join(file_names)}*"

        st.session_state.messages.append({"role": "user", "content": display_message})
        with st.chat_message("user"):
            st.markdown(display_message)

        if st.session_state.thread_id and openai_client and assistant_id:
            try:
                response = send_message_with_document_context(
                    openai_client,
                    st.session_state.thread_id,
                    assistant_id,
                    user_text,
                    current_doc_contents=current_doc_contents,
                )

                if response:
                    st.session_state.messages.append(response)
                    with st.chat_message("assistant"):
                        st.markdown(response["content"])
                else:
                    st.error("No se pudo obtener respuesta. Por favor, intente de nuevo.")
            except Exception as e:
                st.error(f"Error al procesar la respuesta: {str(e)}")
                logging.error(f"Error procesando respuesta: {traceback.format_exc()}")
        else:
            st.error("Error: Sistema no inicializado correctamente.")
