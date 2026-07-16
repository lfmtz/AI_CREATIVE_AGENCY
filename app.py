import os
import glob
import time
from PIL import Image
import streamlit as st
import google.generativeai as genai
from rembg import remove

# Configuración visual de la plataforma web
st.set_page_config(page_title="Agencia IA - Motor Multimodal Real", page_icon="🚀", layout="wide")

st.title("🤖 Ecosistema de Coworking - Agencia Creativa IA")
st.subheader("Orquestador Multimodal: Edición y Generación de Artes Reales en Lote")

# 1. Configuración de API Key en la barra lateral
st.sidebar.header("🔑 Configuración")
api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")
st.sidebar.markdown("[¿Cómo obtener una API Key gratis?](https://aistudio.google.com/)")

# Definición de rutas del ecosistema
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_DIR = os.path.join(BASE_DIR, "00_INVENTORY_IMAGES")
OUTPUT_DIR = os.path.join(BASE_DIR, "10_PROJECTS", "Campana_Automatizada")

def cargar_markdown(ruta_relativa):
    ruta_completa = os.path.join(BASE_DIR, ruta_relativa)
    if os.path.exists(ruta_completa):
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def llamar_gema_texto(prompt_sistema, entrada_usuario):
    ultimo_error = None
    # Probamos los modelos principales de texto en cascada
    for model_name in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-2.5-flash"]:
        for intento in range(3):
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=prompt_sistema
                )
                response = model.generate_content(entrada_usuario)
                return response.text
            except Exception as e:
                ultimo_error = e
                # Si es un error de rate limit (429), esperamos y reintentamos con el mismo modelo
                if "429" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower() or "exhausted" in str(e).lower():
                    wait_time = (intento + 1) * 3
                    st.warning(f"⏳ Límite de velocidad (429) con '{model_name}'. Esperando {wait_time}s para reintentar (Intento {intento + 1}/3)...")
                    time.sleep(wait_time)
                    continue
                else:
                    st.warning(f"⚠️ El modelo '{model_name}' falló. Detalle: {str(e)}. Probando con el siguiente...")
                    break
    st.error(f"❌ Todos los modelos de texto de Gemini fallaron. Último error: {str(ultimo_error)}")
    raise ultimo_error

# Caja de texto para la orden del usuario
idea_usuario = st.text_area(
    "💡 Describe tu requerimiento o campaña:",
    placeholder="Ej: Necesito una imagen para mi estado de WhatsApp de una RAM 1200 chasis con fondo alusivo a la marca..."
)

# Escanear imágenes disponibles en el inventario
if not os.path.exists(INVENTORY_DIR):
    os.makedirs(INVENTORY_DIR, exist_ok=True)

# Listar archivos físicos en el inventario (útil para diagnóstico en Streamlit Cloud)
archivos_fisicos = [f for f in os.listdir(INVENTORY_DIR) if f != "README_INVENTORY.md"]
if archivos_fisicos:
    st.sidebar.write("Archivos en inventario:", archivos_fisicos)

# Glob insensible a mayúsculas/minúsculas para Linux (Streamlit Cloud)
imagenes_locales = []
for patron in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
    imagenes_locales.extend(glob.glob(os.path.join(INVENTORY_DIR, patron)))

st.sidebar.markdown(f"📦 **Inventario detectado:** {len(imagenes_locales)} imágenes.")

if st.button("🚀 Iniciar Trabajo en Cadena Multimodal"):
    if not api_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral.")
    elif not idea_usuario:
        st.warning("Escribe una orden antes de ejecutar.")
    else:
        try:
            genai.configure(api_key=api_key)
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            contexto_auto = cargar_markdown("00_SHARED_KNOWLEDGE/Automotive/automotive_rules.md")
            contexto_copy = cargar_markdown("00_SHARED_KNOWLEDGE/Copywriting/copywriting_guidelines.md")
            contexto_media = cargar_markdown("00_SHARED_KNOWLEDGE/Social_Media/media_specs.md")
            contexto_global = f"\n{contexto_auto}\n{contexto_copy}\n{contexto_media}"
            
            with st.status("Ejecutando agentes y procesando artes en lote...", expanded=True) as status:
                
                # FASE 1: Director Creativo (Estrategia rápida si es requerida)
                st.write("👤 **[1/5] Ejecutando:** Creative Director Pro...")
                time.sleep(2)
                kb_director = cargar_markdown("01_CREATIVE_DIRECTOR/creative_director_pro.md")
                brief = llamar_gema_texto(kb_director + contexto_global, idea_usuario)
                
                # FASE 2: Diseñador Gráfico (Dirección de Arte y especificación de fondo)
                st.write("🎨 **[2/5] Ejecutando:** Graphic Designer Pro...")
                time.sleep(2)
                kb_designer = cargar_markdown("02_GRAPHIC_DESIGNER/graphic_designer_pro.md")
                arte = llamar_gema_texto(kb_designer + contexto_global, f"Crea las directrices visuales del fondo ideal de la marca para esta solicitud: {idea_usuario}")
                
                # FASE 3: Copywriter Pro (Redacta el copy solicitado)
                st.write("✍️ **[3/5] Ejecutando:** Copywriter Pro...")
                time.sleep(2)
                kb_copy = cargar_markdown("06_COPYWRITER/copywriter_pro.md")
                textos = llamar_gema_texto(kb_copy + contexto_global, f"Redacta el copy solicitado en la orden: {idea_usuario}")
                
                # FASE 4: Visual Automation Expert (Crea el Prompt para el Generador de Fondos)
                st.write("📐 **[4/5] Ejecutando:** Visual Automation Expert...")
                time.sleep(2)
                kb_visual = cargar_markdown("03_B_VISUAL_AUTOMATION/visual_automation_expert.md")
                manifiesto_diseno = llamar_gema_texto(kb_visual + contexto_global, f"Escribe un prompt fotográfico ultra-detallado de 1080x1920 px para generar SOLO EL FONDO de la marca solicitada basándote en: {arte}. No incluyas ningún coche en la descripción del fondo.")
                
                # FASE 5: Motor de Montaje Físico (Nanobana + Pillow + rembg)
                lista_artes_finales = []
                # FASE 5: Motor de Montaje Físico (Nanobana + Pillow + rembg)
                st.write("📸 **[5/5] Renderizando fondos con Nanobana...**")
                time.sleep(2)
                
                try:
                    # 1. Generamos el fondo corporativo premium una sola vez para la marca solicitada
                    st.write("🌌 Generando fondo de marca de alta gama con Imagen 3...")
                    imagen_modelo = genai.ImageGenerationModel("imagen-3.0-generate-002")
                    
                    resultado_fondo = None
                    ultimo_err_imagen = None
                    for intento in range(3):
                        try:
                            resultado_fondo = imagen_modelo.generate_images(
                                prompt=f"A professional, commercial-grade background, vertical format (1080x1920 px), clean studio or outdoor setting designed for a car advertisement. Description: {manifiesto_diseno}",
                                number_of_images=1,
                                aspect_ratio="9:16"
                            )
                            break
                        except Exception as img_err:
                            ultimo_err_imagen = img_err
                            if "429" in str(img_err) or "quota" in str(img_err).lower() or "limit" in str(img_err).lower():
                                st.warning(f"⏳ Límite de velocidad en generación de imágenes. Esperando 5s...")
                                time.sleep(5)
                                continue
                            else:
                                break
                                
                    if resultado_fondo is None:
                        raise ultimo_err_imagen
                    
                    # Guardamos el fondo maestro generado por la IA
                    ruta_fondo_maestro = os.path.join(OUTPUT_DIR, "fondo_generado_maestro.png")
                    resultado_fondo.images[0].save(ruta_fondo_maestro)
                    
                    # Si hay imágenes en el inventario, hacemos la fusión física
                    if len(imagenes_locales) > 0:
                        fondo_maestro = Image.open(ruta_fondo_maestro).convert("RGBA")
                        # Procesamos cada carro del inventario en lote
                        for idx, ruta_img in enumerate(imagenes_locales):
                            nombre_archivo = os.path.basename(ruta_img)
                            st.write(f"✂️ Removiendo fondo y montando vehículo ({idx+1}/{len(imagenes_locales)}): {nombre_archivo}")
                            
                            # Abrimos el coche real
                            img_auto_original = Image.open(ruta_img).convert("RGBA")
                            
                            # Recortamos el fondo original de tu coche usando la librería rembg
                            img_auto_recortado = remove(img_auto_original)
                            
                            # Redimensionamos el coche recortado para que quepa estéticamente en el lienzo vertical (1080x1920)
                            ancho_canvas, alto_canvas = fondo_maestro.size
                            img_auto_recortado.thumbnail((ancho_canvas * 0.9, alto_canvas * 0.4))
                            
                            # Creamos una copia del fondo maestro para no encimar los carros uno sobre otro
                            canvas_final = fondo_maestro.copy()
                            
                            # Calculamos la posición para centrar el auto en la mitad inferior
                            pos_x = int((ancho_canvas - img_auto_recortado.width) / 2)
                            pos_y = int(alto_canvas * 0.5)  # Posición vertical centrada-baja
                            
                            # Fusionamos el coche sobre el fondo de la marca
                            canvas_final.paste(img_auto_recortado, (pos_x, pos_y), img_auto_recortado)
                            
                            # Guardamos el archivo final descargable
                            ruta_salida_final = os.path.join(OUTPUT_DIR, f"arte_final_{nombre_archivo}")
                            canvas_final.save(ruta_salida_final)
                            
                            lista_artes_finales.append((f"🎯 Arte Terminado para {nombre_archivo}", ruta_salida_final))
                    else:
                        # Si no hay imágenes en el inventario, entregamos el fondo generado directamente
                        st.info("ℹ️ No se detectaron coches en el inventario. Entregando el fondo de marca premium generado.")
                        lista_artes_finales.append(("🎯 Fondo de Marca Premium Generado (Listo para montaje)", ruta_fondo_maestro))
                        
                except Exception as e:
                    st.error(f"Error en el motor de montaje o generación: {str(e)}")
                    
                status.update(label="🎉 ¡Procesamiento de catálogo finalizado con éxito!", state="complete", expanded=False)
                
            # Despliegue en pestañas organizadas dentro de la UI
            st.success("✨ Tus entregables solicitados están listos:")
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📝 Estrategia/Brief", 
                "🎨 Dirección de Arte", 
                "✍️ Copies Solicitados", 
                "📐 Especificaciones Técnicas",
                "🖼️ Catálogo de Artes Listas para WhatsApp"
            ])
            
            with tab1: st.markdown(brief)
            with tab2: st.markdown(arte)
            with tab3: st.markdown(textos)
            with tab4: st.markdown(manifiesto_diseno)
            with tab5:
                if lista_artes_finales:
                    st.info("💡 ¡Haz clic derecho sobre cualquier arte para guardarla y subirla a tus estados!")
                    for titulo, ruta_final in lista_artes_finales:
                        st.subheader(titulo)
                        st.image(ruta_final, width=360)
                        st.markdown("---")
                else:
                    st.info("Coloca fotos en '00_INVENTORY_IMAGES/' para activar el catálogo visual.")
        except Exception as main_err:
            st.error("💥 **Error Crítico en la ejecución del pipeline:**")
            status_code = getattr(main_err, 'status_code', None) or getattr(main_err, 'code', None)
            st.code(f"Tipo: {type(main_err).__name__}\nCódigo: {status_code}\nDetalles: {str(main_err)}")
            response = getattr(main_err, 'response', None)
            if response:
                st.code(f"Respuesta del Servidor:\n{getattr(response, 'text', '')}")
            raise main_err