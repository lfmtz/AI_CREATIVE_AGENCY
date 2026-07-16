import os
import argparse
import glob
from PIL import Image
from google import genai
from google.genai import types

# Definición de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_DIR = os.path.join(BASE_DIR, "00_INVENTORY_IMAGES")

def cargar_markdown(ruta_relativa):
    ruta_completa = os.path.join(BASE_DIR, ruta_relativa)
    if os.path.exists(ruta_completa):
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def llamar_gema_texto(client, prompt_sistema, entrada_usuario):
    ultimo_error = None
    for model_name in ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=entrada_usuario,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema
                )
            )
            return response.text
        except Exception as e:
            ultimo_error = e
            print(f"⚠️ El modelo '{model_name}' falló. Reintentando...")
    raise ultimo_error

def main():
    parser = argparse.ArgumentParser(description="Test campaign generation pipeline")
    parser.add_argument("--api-key", help="Gemini API Key", required=True)
    args = parser.parse_args()

    client = genai.Client(api_key=args.api_key)

    idea_usuario = "necesito una imagen para whatsapp para mi estado, maneja un fondo de acuerdo a la marca de la imagen ram 1200 chasis"
    print(f"💡 Orden del usuario: '{idea_usuario}'\n")

    # Cargar el contexto de reglas base (.md)
    contexto_auto = cargar_markdown("00_SHARED_KNOWLEDGE/Automotive/automotive_rules.md")
    contexto_copy = cargar_markdown("00_SHARED_KNOWLEDGE/Copywriting/copywriting_guidelines.md")
    contexto_media = cargar_markdown("00_SHARED_KNOWLEDGE/Social_Media/media_specs.md")
    contexto_global = f"\n{contexto_auto}\n{contexto_copy}\n{contexto_media}"

    # Paso 0: Clasificación inteligente de la orden
    print("🧠 [Configuración] Evaluando si requiere Brief...")
    prompt_filtro = f"Analiza esta orden: '{idea_usuario}'. Responde en una sola palabra 'SI' si requiere un Brief y estrategia conceptual profunda, o 'NO' si es una orden directa y operativa."
    requiere_brief = llamar_gema_texto(client, contexto_global, prompt_filtro).strip().upper()
    print(f"-> Requiere Brief: {requiere_brief}\n")

    # FASE 1: Director Creativo
    if "SI" in requiere_brief:
        print("👤 [1/5] Ejecutando: Creative Director Pro...")
        kb_director = cargar_markdown("01_CREATIVE_DIRECTOR/creative_director_pro.md")
        brief = llamar_gema_texto(client, kb_director + contexto_global, idea_usuario)
    else:
        print("⏭️ [1/5] Director Creativo: Omitido (Orden operativa directa).")
        brief = f"Orden Directa: {idea_usuario}"
    print(f"--- BRIEF RESULTANTE ---\n{brief}\n")

    # FASE 2: Diseñador Gráfico
    print("🎨 [2/5] Ejecutando: Graphic Designer Pro...")
    kb_designer = cargar_markdown("02_GRAPHIC_DESIGNER/graphic_designer_pro.md")
    arte = llamar_gema_texto(client, kb_designer + contexto_global, f"Establece los lineamientos visuales exclusivamente para lo solicitado en esta orden: {idea_usuario}\nContexto base: {brief}")
    print(f"--- DIRECCIÓN DE ARTE ---\n{arte}\n")

    # FASE 3: Copywriter Pro
    print("✍️ [3/5] Ejecutando: Copywriter Pro...")
    kb_copy = cargar_markdown("06_COPYWRITER/copywriter_pro.md")
    textos = llamar_gema_texto(client, kb_copy + contexto_global, f"Escribe única y exclusivamente los copys solicitados para las redes especificadas en la orden: {idea_usuario}. No inventes otros formatos.")
    print(f"--- COPIES ---\n{textos}\n")

    # FASE 4: Visual Automation Expert
    print("📐 [4/5] Ejecutando: Visual Automation Expert...")
    kb_visual = cargar_markdown("03_B_VISUAL_AUTOMATION/visual_automation_expert.md")
    manifiesto_diseno = llamar_gema_texto(client, kb_visual + contexto_global, f"Genera las instrucciones técnicas y coordenadas métricas basándote solo en los formatos pedidos en: {idea_usuario}.")
    print(f"--- MANIFIESTO DE DISEÑO ---\n{manifiesto_diseno}\n")

    # FASE 5: Motor Multimodal
    imagenes_locales = glob.glob(os.path.join(INVENTORY_DIR, "*.jpg")) + \
                       glob.glob(os.path.join(INVENTORY_DIR, "*.jpeg")) + \
                       glob.glob(os.path.join(INVENTORY_DIR, "*.png"))
    
    print(f"📦 Inventario detectado: {len(imagenes_locales)} imágenes.")
    if len(imagenes_locales) > 0 and any(keyword in idea_usuario.lower() for keyword in ["imagen", "arte", "catalogo", "foto", "diseño"]):
        print("📸 [5/5] Ejecutando: Procesamiento Multimodal en lote sobre imágenes...")
        for idx, ruta_img in enumerate(imagenes_locales):
            nombre_archivo = os.path.basename(ruta_img)
            print(f"-> Procesando: {nombre_archivo}")
            try:
                imagen_pil = Image.open(ruta_img)
                instruccion_nanobana = f"Procesa visualmente este coche aplicando de forma estricta los formatos solicitados en la orden: {idea_usuario}. Siguiendo este manifiesto: {manifiesto_diseno}"
                
                respuesta_visual = None
                ultimo_err_visual = None
                for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-3.5-flash"]:
                    try:
                        respuesta_visual = client.models.generate_content(
                            model=model_name,
                            contents=[instruccion_nanobana, imagen_pil]
                        )
                        break
                    except Exception as model_err:
                        ultimo_err_visual = model_err
                        print(f"  ⚠️ Falló {model_name} para {nombre_archivo}. Probando alternativo...")
                
                if respuesta_visual is None:
                    raise ultimo_err_visual
                print(f"\n--- REPORTE VISUAL PARA {nombre_archivo} ---\n{respuesta_visual.text}\n")
            except Exception as e:
                print(f"❌ Error procesando {nombre_archivo}: {e}")
    else:
        print("⏭️ [5/5] Motor Multimodal: Omitido.")

if __name__ == "__main__":
    main()
