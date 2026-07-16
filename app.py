import os
import time
from PIL import Image
import streamlit as st
import google.generativeai as genai
from rembg import remove

# --- FORZAR LA VERSIÓN V1 DE LA API DE GOOGLE PARA EVITAR ERRORES 404 V1BETA ---
os.environ["API_VERSION"] = "v1"

# Configuración de página universal
st.set_page_config(page_title="Agencia Creativa IA Universal", page_icon="🚀", layout="wide")

st.title("🤖 Ecosistema de Coworking - Agencia Creativa IA")
st.subheader("Orquestador Multimodal Adaptable: Post, Historias y Banners a la Carta")

# Barra lateral para credenciales y visor de archivos
st.sidebar.header("🔑 Configuración")
api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")
st.sidebar.markdown("[¿Cómo obtener una API Key gratis?](https://aistudio.google.com/)")

# Definición de rutas directa adaptada a Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_DIR = os.path.join(BASE_DIR, "00_INVENTORY_IMAGES")
OUTPUT_DIR = os.path.join(BASE_DIR, "10_PROJECTS", "Campana_Automatizada")

# Garantizar que las carpetas existan
os.makedirs(INVENTORY_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- VISOR EXPLORADOR DE ARCHIVOS EN VIVO (LADO IZQUIERDO) ---
st.sidebar.markdown("---")
st.sidebar.markdown("📁 **Explorador de Archivos en el Servidor:**")
def mostrar_arbol_archivos(ruta_base):
    try:
        for elemento in sorted(os.listdir(ruta_base)):
            if elemento.startswith('.') or elemento == "__pycache__":
                continue
            ruta_completa = os.path.join(ruta_base, elemento)
            if os.path.isdir(ruta_completa):
                with st.sidebar.expander(f"📁 {elemento}", expanded=False):
                    mostrar_arbol_archivos(ruta_completa)
            else:
                st.text(f"📄 {elemento}")
    except Exception:
        st.text("No se pudo leer el directorio raíz.")

mostrar_arbol_archivos(BASE_DIR)
st.sidebar.markdown("---")

# Escaneo directo de imágenes del inventario
imagenes_locales = []
if os.path.exists(INVENTORY_DIR):
    for f in os.listdir(INVENTORY_DIR):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('.'):
            imagenes_locales.append(os.path.join(INVENTORY_DIR, f))

st.sidebar.markdown(f"📦 **Inventario en la nube:** {len(imagenes_locales)} imágenes detectadas.")

def cargar_markdown(ruta_relativa):
    ruta_completa = os.path.join(BASE_DIR, ruta_relativa)
    if os.path.exists(ruta_completa):
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def llamar_gema_texto(prompt_sistema, entrada_usuario):
    ultimo_error = None
    # Cascada de modelos para saltar límites diarios o saturaciones de un modelo específico
    modelos_a_probar = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"]
    for model_name in modelos_a_probar:
        for intento in range(3):
            try:
                model = genai.GenerativeModel(model_name=model_name, system_instruction=prompt_sistema)
                response = model.generate_content(entrada_usuario)
                return response.text
            except Exception as e:
                ultimo_error = e
                # Si es un límite de cuota o rate limit
                if "429" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower() or "exhausted" in str(e).lower():
                    # Si es un límite diario estricto (ej. el límite diario de 20 peticiones agotado)
                    # pasamos inmediatamente al siguiente modelo
                    if "day" in str(e).lower() or "daily" in str(e).lower() or "project" in str(e).lower():
                        st.warning(f"⚠️ Límite diario excedido para '{model_name}'. Probando el siguiente modelo en cascada...")
                        break
                    
                    wait_time = (intento + 1) * 3
                    st.warning(f"⏳ Límite de velocidad (429) con '{model_name}'. Esperando {wait_time}s para reintentar (Intento {intento + 1}/3)...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Otros errores como modelo no soportado
                    break
    st.error(f"❌ Todos los modelos de texto de Gemini fallaron. Último error: {str(ultimo_error)}")
    raise ultimo_error

# Cuadro de texto libre para cualquier canal o red social
idea_usuario = st.text_area(
    "💡 ¿Qué pieza publicitaria necesitas hoy?",
    placeholder="Ej: Necesito una imagen para mi historia en whatsapp, esta debe de ir vertical, la camioneta horizontal, con un fondo alusivo al trabajo en ram y que diga Ram 1200 chasis y que diga prueba de éxito..."
)

if st.button("🚀 Iniciar Cadena Multimodal"):
    if not api_key:
        st.error("Por favor, introduce tu Gemini API Key en la barra lateral.")
    elif not idea_usuario:
        st.warning("Por favor, escribe las instrucciones de tu post, banner o historia.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Cargar base de conocimiento
            contexto_auto = cargar_markdown("00_SHARED_KNOWLEDGE/Automotive/automotive_rules.md")
            contexto_copy = cargar_markdown("00_SHARED_KNOWLEDGE/Copywriting/copywriting_guidelines.md")
            contexto_media = cargar_markdown("00_SHARED_KNOWLEDGE/Social_Media/media_specs.md")
            contexto_global = f"\n{contexto_auto}\n{contexto_copy}\n{contexto_media}"
            
            # --- DETECCIÓN INTELIGENTE DE MEDIDAS Y RELACIÓN DE ASPECTO ---
            texto_analisis = idea_usuario.lower()
            if any(w in texto_analisis for w in ["historia", "whatsapp", "story", "vertical", "reel"]):
                aspecto_ia = "9:16"
                ancho_canvas, alto_canvas = 1080, 1920
                tipo_formato = "Historia / Estado Vertical"
            elif any(w in texto_analisis for w in ["banner", "horizontal", "portada", "web"]):
                aspecto_ia = "16:9"
                ancho_canvas, alto_canvas = 1920, 1080
                tipo_formato = "Banner Horizontal"
            else:
                # Por defecto genera formato cuadrado adaptable para posts de Facebook/Instagram
                aspecto_ia = "1:1"
                ancho_canvas, alto_canvas = 1080, 1080
                tipo_formato = "Post Cuadrado Tradicional"

            with st.status(f"Procesando formato: {tipo_formato}...", expanded=True) as status:
                
                # FASE 1: Director Creativo
                st.write("👤 **[1/5] Ejecutando:** Creative Director Pro...")
                time.sleep(2)
                kb_director = cargar_markdown("01_CREATIVE_DIRECTOR/creative_director_pro.md")
                brief = llamar_gema_texto(kb_director + contexto_global, idea_usuario)
                
                # FASE 2: Diseñador Gráfico (Dirección de Arte adaptable)
                st.write("🎨 **[2/5] Ejecutando:** Graphic Designer Pro...")
                time.sleep(2)
                kb_designer = cargar_markdown("02_GRAPHIC_DESIGNER/graphic_designer_pro.md")
                arte = llamar_gema_texto(kb_designer + contexto_global, f"Define los colores y el estilo visual para un formato {tipo_formato} basado en: {idea_usuario}")
                
                # FASE 3: Copywriter Pro
                st.write("✍️ **[3/5] Ejecutando:** Copywriter Pro...")
                time.sleep(2)
                kb_copy = cargar_markdown("06_COPYWRITER/copywriter_pro.md")
                textos = llamar_gema_texto(kb_copy + contexto_global, f"Genera los copies y textos integrados exactos solicitados para este formato: {idea_usuario}")
                
                # FASE 4: Visual Automation Expert (Prompt del Fondo)
                st.write("📐 **[4/5] Ejecutando:** Visual Automation Expert...")
                time.sleep(2)
                kb_visual = cargar_markdown("03_B_VISUAL_AUTOMATION/visual_automation_expert.md")
                manifiesto_diseno = llamar_gema_texto(kb_visual + contexto_global, f"Escribe un prompt de generación de imagen para el FONDO comercial de la marca en relación {aspecto_ia}. Instrucciones: {idea_usuario}. No incluyas vehículos en la descripción.")
                
                # FASE 5: Composición Multimodal Real y Universal
                lista_artes_finales = []
                st.write(f"🌌 Generando fondo premium adaptado ({aspecto_ia}) con Nanobana...")
                time.sleep(2)
                try:
                    imagen_modelo = genai.ImageGenerationModel("imagen-3.0-generate-002")
                    
                    resultado_fondo = None
                    ultimo_err_imagen = None
                    for intento in range(3):
                        try:
                            resultado_fondo = imagen_modelo.generate_images(
                                prompt=f"A professional high-end commercial ad background, layout {aspecto_ia}, sharp focus, studio lighting. Description: {manifiesto_diseno}",
                                number_of_images=1,
                                aspect_ratio=aspecto_ia
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
                    
                    ruta_fondo = os.path.join(OUTPUT_DIR, "fondo_base.png")
                    resultado_fondo.images[0].save(ruta_fondo)
                    
                    if len(imagenes_locales) > 0:
                        fondo_maestro = Image.open(ruta_fondo).convert("RGBA")
                        fondo_maestro = fondo_maestro.resize((ancho_canvas, alto_canvas))
                        
                        for idx, ruta_img in enumerate(imagenes_locales):
                            nombre_archivo = os.path.basename(ruta_img)
                            st.write(f"✂️ Extrayendo y fusionando vehículo sobre {tipo_formato}: {nombre_archivo}")
                            
                            img_original = Image.open(ruta_img).convert("RGBA")
                            img_recortada = remove(img_original)
                            
                            # Ajustar el tamaño del coche de forma proporcional al lienzo elegido
                            if aspecto_ia == "9:16":
                                img_recortada.thumbnail((ancho_canvas * 0.9, alto_canvas * 0.35))
                                pos_x = int((ancho_canvas - img_recortada.width) / 2)
                                pos_y = int(alto_canvas * 0.55)
                            else:
                                img_recortada.thumbnail((ancho_canvas * 0.65, alto_canvas * 0.6))
                                pos_x = int((ancho_canvas - img_recortada.width) / 2)
                                pos_y = int((alto_canvas - img_recortada.height) / 2)
                                
                            canvas_final = fondo_maestro.copy()
                            canvas_final.paste(img_recortada, (pos_x, pos_y), img_recortada)
                            
                            ruta_salida = os.path.join(OUTPUT_DIR, f"arte_final_{nombre_archivo}")
                            canvas_final.save(ruta_salida)
                            lista_artes_finales.append((f"🎯 Arte Terminado ({tipo_formato}): {nombre_archivo}", ruta_salida))
                    else:
                        st.info("ℹ️ No se detectaron coches en el inventario. Entregando el fondo de marca premium generado.")
                        lista_artes_finales.append((f"🎯 Fondo de Marca Premium Generado ({tipo_formato})", ruta_fondo))
                        
                except Exception as e:
                    st.error(f"Error en el motor visual: {str(e)}")
                
                status.update(label="🎉 ¡Entrega universal finalizada con éxito!", state="complete", expanded=False)
                
            # Despliegue de resultados organizados
            st.success("✨ Tus entregables solicitados están listos:")
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📝 Estrategia/Brief", "🎨 Dirección de Arte", "✍️ Copies Solicitados", "📐 Especificaciones Técnicas", "🖼️ Arte Publicitario Terminado"
            ])
            
            with tab1: st.markdown(brief)
            with tab2: st.markdown(arte)
            with tab3: st.markdown(textos)
            with tab4: st.markdown(manifiesto_diseno)
            with tab5:
                if lista_artes_finales:
                    st.info("💡 ¡Haz clic derecho sobre el arte para guardarla directamente!")
                    for titulo, ruta_final in lista_artes_finales:
                        st.subheader(titulo)
                        st.image(ruta_final)
                        st.markdown("---")
                else:
                    st.info("No se procesaron imágenes debido a un problema con el archivo base.")
        except Exception as main_err:
            st.error("💥 **Error Crítico en la ejecución del pipeline:**")
            status_code = getattr(main_err, 'status_code', None) or getattr(main_err, 'code', None)
            st.code(f"Tipo: {type(main_err).__name__}\nCódigo: {status_code}\nDetalles: {str(main_err)}")
            response = getattr(main_err, 'response', None)
            if response:
                st.code(f"Respuesta del Servidor:\n{getattr(response, 'text', '')}")
            raise main_err