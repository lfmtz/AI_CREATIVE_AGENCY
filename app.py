import os
import glob
from PIL import Image
from io import BytesIO
import streamlit as st
from google import genai
from google.genai import types

# Configuración visual de la plataforma web
st.set_page_config(page_title="Agencia IA - Motor Multimodal", page_icon="🚀", layout="wide")

st.title("🤖 Ecosistema de Coworking - Agencia Creativa IA")
st.subheader("Orquestador Masivo Multimodal: Generación de Artes en Lote para WhatsApp")

# 1. Configuración de API Key en la barra lateral
st.sidebar.header("🔑 Configuración")
api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")
st.sidebar.markdown("[¿Cómo obtener una API Key gratis?](https://aistudio.google.com/)")

# Definición de rutas absolutas del ecosistema
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_DIR = os.path.join(BASE_DIR, "00_INVENTORY_IMAGES")
OUTPUT_DIR = os.path.join(BASE_DIR, "10_PROJECTS", "Campana_Automatizada")

def cargar_markdown(ruta_relativa):
    """Lee las bases de conocimiento (.md) de las carpetas de tus gemas"""
    ruta_completa = os.path.join(BASE_DIR, ruta_relativa)
    if os.path.exists(ruta_completa):
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def llamar_gema_texto(client, prompt_sistema, entrada_usuario):
    """Conexión estándar para las gemas estratégicas de texto"""
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=entrada_usuario,
        config=types.GenerateContentConfig(
            system_instruction=prompt_sistema
        )
    )
    return response.text

def llamar_gema_multimodal(client, prompt_sistema, entrada_texto, objeto_imagen):
    """Conexión avanzada con el modelo para procesar la imagen del vehículo real"""
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[entrada_texto, objeto_imagen],
        config=types.GenerateContentConfig(
            system_instruction=prompt_sistema
        )
    )
    return response.text

# 2. Entrada de la campaña publicitaria
idea_usuario = st.text_area(
    "💡 Describe la oferta o idea del vehículo para la campaña:",
    placeholder="Ej: Lanzar pauta para RAM 700 en CDMX. Destacar bono de $30,000 MXN y mensualidades desde $3,999 MXN para WhatsApp Status..."
)

# Escanear imágenes disponibles en la carpeta de inventario
imagenes_locales = glob.glob(os.path.join(INVENTORY_DIR, "*.jpg")) + \
                   glob.glob(os.path.join(INVENTORY_DIR, "*.jpeg")) + \
                   glob.glob(os.path.join(INVENTORY_DIR, "*.png"))

st.sidebar.markdown(f"📦 **Inventario detectado:** {len(imagenes_locales)} imágenes listas para procesar.")
archivos_inventario = [f for f in os.listdir(INVENTORY_DIR) if f != "README_INVENTORY.md"]
if archivos_inventario:
    for f in archivos_inventario:
        icono = "🖼️" if f.lower().endswith(('.png', '.jpg', '.jpeg')) else "📄"
        st.sidebar.markdown(f"- {icono} `{f}`")

# 3. Botón de ejecución en lote
if st.button("🚀 Iniciar Trabajo en Cadena Multimodal"):
    if not api_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral para continuar.")
    elif not idea_usuario:
        st.warning("Escribe una idea o promoción antes de ejecutar a los agentes.")
    else:
        # Inicializar credenciales globales de Google GenAI
        client = genai.Client(api_key=api_key)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Cargar el contexto global corporativo compartido (.md)
        contexto_auto = cargar_markdown("00_SHARED_KNOWLEDGE/Automotive/automotive_rules.md")
        contexto_copy = cargar_markdown("00_SHARED_KNOWLEDGE/Copywriting/copywriting_guidelines.md")
        contexto_media = cargar_markdown("00_SHARED_KNOWLEDGE/Social_Media/media_specs.md")
        contexto_global = f"\n{contexto_auto}\n{contexto_copy}\n{contexto_media}"
        
        # Flujo de ejecución secuencial de agentes
        with st.status("Ejecutando pipeline y procesando imágenes en lote...", expanded=True) as status:
            
            # FASE 1: Creative Director Pro
            st.write("👤 **[1/5] Ejecutando:** Creative Director Pro...")
            kb_director = cargar_markdown("01_CREATIVE_DIRECTOR/creative_director_pro.md")
            brief = llamar_gema_texto(client, kb_director + contexto_global, idea_usuario)
            
            # FASE 2: Graphic Designer Pro
            st.write("👤 **[2/5] Ejecutando:** Graphic Designer Pro...")
            kb_designer = cargar_markdown("02_GRAPHIC_DESIGNER/graphic_designer_pro.md")
            arte = llamar_gema_texto(client, kb_designer + contexto_global, f"Genera la dirección de arte basada en este Brief:\n\n{brief}")
            
            # FASE 3: Copywriter Pro
            st.write("👤 **[3/5] Ejecutando:** Copywriter Pro...")
            kb_copy = cargar_markdown("06_COPYWRITER/copywriter_pro.md")
            textos = llamar_gema_texto(client, kb_copy + contexto_global, f"Escribe los copys usando:\nBrief:\n{brief}\n\nArte:\n{arte}")
            
            # FASE 4: Visual Automation Expert
            st.write("🤖 **[4/5] Ejecutando:** Visual Automation Expert...")
            kb_visual = cargar_markdown("03_B_VISUAL_AUTOMATION/visual_automation_expert.md")
            manifiesto_diseno = llamar_gema_texto(client, kb_visual + contexto_global, f"Genera las instrucciones técnicas usando:\nDirección de arte:\n{arte}\n\nCopies:\n{textos}")
            
            # FASE 5: Generación y Renderizado de Imagen Real
            st.write("📸 **[5/5] Generando Artes Visuales finales con motor de imágenes...**")
            lista_artes_finales = []
            
            if len(imagenes_locales) == 0:
                st.warning("No se encontraron archivos de imagen en la carpeta '00_INVENTORY_IMAGES/'.")
            else:
                for idx, ruta_img in enumerate(imagenes_locales):
                    nombre_archivo = os.path.basename(ruta_img)
                    st.write(f"🎨 Renderizando banner para: {nombre_archivo}")
                    
                    # Definimos el prompt visual final uniendo el manifiesto y el formato vertical de WhatsApp
                    prompt_visual_final = f"Un banner publicitario profesional en formato vertical (relación de aspecto 9:16, 1080x1920 píxeles) para estados de WhatsApp. Basado en este vehículo e instrucciones: {manifiesto_diseno}. Reemplaza el fondo por un entorno premium de la marca con iluminación realista y reflejos automotrices sobre la carrocería."
                    
                    try:
                        # Invocamos al modelo de generación de imágenes de Google
                        resultado_imagen = client.models.generate_images(
                            model="imagen-3.0-generate-002",
                            prompt=prompt_visual_final,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                aspect_ratio="9:16"
                            )
                        )
                        
                        # Extraemos la imagen generada y la guardamos localmente
                        for imagen_generada in resultado_imagen.generated_images:
                            ruta_guardado = os.path.join(OUTPUT_DIR, f"arte_whatsapp_{nombre_archivo}")
                            # Convertimos los bytes en imagen PIL y la guardamos
                            imagen_pil = Image.open(BytesIO(imagen_generada.image.image_bytes))
                            imagen_pil.save(ruta_guardado)
                            lista_artes_finales.append((f"Arte para {nombre_archivo}", ruta_guardado))
                    except Exception as e:
                        st.error(f"Error al generar la imagen para {nombre_archivo}: {str(e)}")

            status.update(label="🎉 ¡Ecosistema finalizado con éxito!", state="complete", expanded=False)

        # [Modificación en el despliegue de pestañas finales]
        st.success("✨ Entregables creativos y técnicos listos:")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Creative Brief", 
            "🎨 Dirección de Arte", 
            "✍️ Copies Persuasivos", 
            "📐 Manifiesto de Estilos",
            "🖼️ Artes Listos para WhatsApp"
        ])
        
        with tab1:
            st.markdown(brief)
        with tab2:
            st.markdown(arte)
        with tab3:
            st.markdown(textos)
        with tab4:
            st.markdown(manifiesto_diseno)
        with tab5:
            if lista_artes_finales:
                for titulo, ruta_final in lista_artes_finales:
                    st.subheader(titulo)
                    st.image(ruta_final, caption="Haz clic derecho sobre la imagen para guardarla en tu celular o PC", use_container_width=False, width=360)
            else:
                st.info("Coloca una foto en '00_INVENTORY_IMAGES/' para ver el arte final aquí.")