import os
import streamlit as st
import google.generativeai as genai

# Configuración visual de la página web
st.set_page_config(page_title="Agencia IA - Coworking", page_icon="🚀", layout="wide")

st.title("🤖 Ecosistema de Coworking - Agencia Creativa IA")
st.subheader("Orquesta tus GEMs en cadena automotriz con un solo clic")

# 1. Barra lateral para la API Key
st.sidebar.header("🔑 Configuración")
api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")
st.sidebar.markdown("[¿Cómo obtener una API Key gratis?](https://aistudio.google.com/)")

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_markdown(ruta_relativa):
    """Función para leer las bases de conocimiento (.md) de tus carpetas"""
    ruta_completa = os.path.join(BASE_DIR, ruta_relativa)
    if os.path.exists(ruta_completa):
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def llamar_gema(prompt_sistema, entrada_usuario):
    """Conexión directa con la API de Gemini usando tu modelo Pro"""
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=prompt_sistema
    )
    response = model.generate_content(entrada_usuario)
    return response.text

# 2. Caja de texto para tu idea de pauta/contenido
idea_usuario = st.text_area(
    "💡 Describe la oferta o idea del vehículo para la campaña:",
    placeholder="Ej: Lanzar pauta para Jeep Grand Cherokee en CDMX. Destacar bono de $50,000 MXN y captar leads para WhatsApp..."
)

# 3. Botón de ejecución del Coworking
if st.button("🚀 Iniciar Trabajo en Cadena"):
    if not api_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral para continuar.")
    elif not idea_usuario:
        st.warning("Escribe una idea o promoción antes de ejecutar a los agentes.")
    else:
        # Configurar la API Key de Google
        genai.configure(api_key=api_key)
        
        # Cargar el Contexto Global de las subcarpetas de la 00
        contexto_auto = cargar_markdown("00_SHARED_KNOWLEDGE/Automotive/automotive_rules.md")
        contexto_copy = cargar_markdown("00_SHARED_KNOWLEDGE/Copywriting/copywriting_guidelines.md")
        contexto_media = cargar_markdown("00_SHARED_KNOWLEDGE/Social_Media/media_specs.md")
        contexto_global = f"\n{contexto_auto}\n{contexto_copy}\n{contexto_media}"
        
        # Animación de progreso en tiempo real
        with st.status("Tu equipo de agentes está trabajando...", expanded=True) as status:
            
            # FASE 1: Creative Director Pro
            st.write("👤 **[1/4] Ejecutando:** Creative Director Pro...")
            kb_director = cargar_markdown("01_CREATIVE_DIRECTOR/creative_director_pro.md")
            brief = llamar_gema(kb_director + contexto_global, idea_usuario)
            
            # FASE 2: Graphic Designer Pro (Toma el Brief resultante)
            st.write("👤 **[2/4] Ejecutando:** Graphic Designer Pro...")
            kb_designer = cargar_markdown("02_GRAPHIC_DESIGNER/graphic_designer_pro.md")
            arte = llamar_gema(kb_designer + contexto_global, f"Genera la dirección de arte basándote en este Brief:\n\n{brief}")
            
            # FASE 3: Copywriter Pro (Toma el Brief y la Dirección de Arte)
            st.write("👤 **[3/4] Ejecutando:** Copywriter Pro...")
            kb_copy = cargar_markdown("06_COPYWRITER/copywriter_pro.md")
            textos = llamar_gema(kb_copy + contexto_global, f"Escribe los copys usando:\nBrief:\n{brief}\n\nArte:\n{arte}")
            
            # FASE 4: Image Prompt Engineer Pro (Toma la Dirección de Arte)
            st.write("👤 **[4/4] Ejecutando:** Image Prompt Engineer Pro...")
            kb_prompter = cargar_markdown("03_IMAGE_PROMPTS/image_prompt_engineer_pro.md")
            prompts_imagenes = llamar_gema(kb_prompter + contexto_global, f"Genera los prompts de IA visual usando esta dirección de arte:\n\n{arte}")
            
            status.update(label="🎉 ¡Entrega lista! Tus agentes han terminado el material.", state="complete", expanded=False)
            
        # 4. Muestra de resultados finales en pestañas interactivas
        st.success("✨ Material publicitario generado con éxito:")
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Creative Brief", "🎨 Dirección de Arte", "✍️ Copies Persuasivos", "🖼️ Prompts de Imágenes"])
        
        with tab1:
            st.markdown(brief)
        with tab2:
            st.markdown(arte)
        with tab3:
            st.markdown(textos)
        with tab4:
            st.markdown(prompts_imagenes)