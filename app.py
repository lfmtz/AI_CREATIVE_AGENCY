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

# 3. Botón de ejecución en lote con Inteligencia Selectiva
if st.button("🚀 Iniciar Trabajo en Cadena Multimodal"):
    if not api_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral para continuar.")
    elif not idea_usuario:
        st.warning("Escribe una orden o promoción antes de ejecutar a los agentes.")
    else:
        client = genai.Client(api_key=api_key)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Cargar el contexto de reglas base (.md)
        contexto_auto = cargar_markdown("00_SHARED_KNOWLEDGE/Automotive/automotive_rules.md")
        contexto_copy = cargar_markdown("00_SHARED_KNOWLEDGE/Copywriting/copywriting_guidelines.md")
        contexto_media = cargar_markdown("00_SHARED_KNOWLEDGE/Social_Media/media_specs.md")
        contexto_global = f"\n{contexto_auto}\n{contexto_copy}\n{contexto_media}"
        
        with st.status("Analizando orden y ejecutando agentes requeridos...", expanded=True) as status:
            
            # Paso 0: Clasificación inteligente de la orden
            st.write("🧠 **[Configuración]** Evaluando canales y entregables solicitados...")
            prompt_filtro = f"Analiza esta orden: '{idea_usuario}'. Responde en una sola palabra 'SI' si requiere un Brief y estrategia conceptual profunda, o 'NO' si es una orden directa y operativa."
            requiere_brief = llamar_gema_texto(client, contexto_global, prompt_filtro).strip().upper()
            
            # FASE 1: Director Creativo (Solo si la estrategia lo amerita)
            if "SI" in requiere_brief:
                st.write("👤 **[1/5] Ejecutando:** Creative Director Pro...")
                kb_director = cargar_markdown("01_CREATIVE_DIRECTOR/creative_director_pro.md")
                brief = llamar_gema_texto(client, kb_director + contexto_global, idea_usuario)
            else:
                st.write("⏭️ **[1/5] Director Creativo:** Omitido (Orden operativa directa).")
                brief = f"Orden Directa: {idea_usuario}"
            
            # FASE 2: Diseñador Gráfico (Dirección de Arte basada estrictamente en la orden)
            st.write("🎨 **[2/5] Ejecutando:** Graphic Designer Pro...")
            kb_designer = cargar_markdown("02_GRAPHIC_DESIGNER/graphic_designer_pro.md")
            arte = llamar_gema_texto(client, kb_designer + contexto_global, f"Establece los lineamientos visuales exclusivamente para lo solicitado en esta orden: {idea_usuario}\nContexto base: {brief}")
            
            # FASE 3: Copywriter Pro (Redacta solo los copys de las redes pedidas)
            st.write("✍️ **[3/5] Ejecutando:** Copywriter Pro...")
            kb_copy = cargar_markdown("06_COPYWRITER/copywriter_pro.md")
            textos = llamar_gema_texto(client, kb_copy + contexto_global, f"Escribe única y exclusivamente los copys solicitados para las redes especificadas en la orden: {idea_usuario}. No inventes otros formatos.")
            
            # FASE 4: Visual Automation Expert (Manifiesto de estilos de los formatos requeridos)
            st.write("📐 **[4/5] Ejecutando:** Visual Automation Expert...")
            kb_visual = cargar_markdown("03_B_VISUAL_AUTOMATION/visual_automation_expert.md")
            manifiesto_diseno = llamar_gema_texto(client, kb_visual + contexto_global, f"Genera las instrucciones técnicas y coordenadas métricas basándote solo en los formatos pedidos en: {idea_usuario}.")
            
            # FASE 5: Motor Multimodal (Solo si se detectan imágenes y se requiere procesamiento visual)
            lista_artes_finales = []
            if len(imagenes_locales) > 0 and any(keyword in idea_usuario.lower() for keyword in ["imagen", "arte", "catalogo", "foto", "diseño"]):
                st.write("📸 **[5/5] Ejecutando:** Procesamiento Multimodal en lote sobre imágenes...")
                for idx, ruta_img in enumerate(imagenes_locales):
                    nombre_archivo = os.path.basename(ruta_img)
                    try:
                        imagen_pil = Image.open(ruta_img)
                        instruccion_nanobana = f"Procesa visualmente este coche aplicando de forma estricta los formatos solicitados en la orden: {idea_usuario}. Siguiendo este manifiesto: {manifiesto_diseno}"
                        respuesta_visual = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[instruccion_nanobana, imagen_pil]
                        )
                        lista_artes_finales.append((f"🚗 Elemento Procesado: {nombre_archivo}", imagen_pil, respuesta_visual.text))
                    except Exception as e:
                        st.error(f"Error procesando {nombre_archivo}: {str(e)}")
            else:
                st.write("⏭️ **[5/5] Motor Multimodal:** Omitido (No se requirió procesamiento visual de imágenes).")
            
            status.update(label="🎉 ¡Entrega a la carta finalizada con éxito!", state="complete", expanded=False)
            
        # Despliegue dinámico en pestañas interactivas de la interfaz
        st.success("✨ Tus entregables solicitados están listos:")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Estrategia/Brief", 
            "🎨 Dirección de Arte", 
            "✍️ Copies Solicitados", 
            "📐 Especificaciones Técnicas",
            "🖼️ Procesamiento Multimodal"
        ])
        
        with tab1: st.markdown(brief)
        with tab2: st.markdown(arte)
        with tab3: st.markdown(textos)
        with tab4: st.markdown(manifiesto_diseno)
        with tab5:
            if lista_artes_finales:
                for titulo, img_origen, reporte_diseno in lista_artes_finales:
                    st.subheader(titulo)
                    st.image(img_origen, width=360)
                    st.info(reporte_diseno)
                    st.markdown("---")
            else:
                st.info("Esta orden no requirió manipulación de imágenes del inventario o la carpeta estaba vacía.")