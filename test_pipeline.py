import os
import sys
import io
import glob
from PIL import Image

# Configurar codificación UTF-8 para consola
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("🔍 INICIANDO TEST DE DIAGNÓSTICO DEL SISTEMA MULTIMODAL...")
print("--------------------------------------------------")

# 1. Verificar existencia de carpetas clave
base_dir = os.path.dirname(os.path.abspath(__file__))
inventory_dir = os.path.join(base_dir, "00_INVENTORY_IMAGES")
output_dir = os.path.join(base_dir, "10_PROJECTS", "Campana_Automatizada")

print(f"📁 Directorio de inventario: {inventory_dir}")
if os.path.exists(inventory_dir):
    print("✅ Carpeta '00_INVENTORY_IMAGES' detectada correctamente.")
else:
    print("❌ ERROR: No se encuentra la carpeta '00_INVENTORY_IMAGES'. Creándola...")
    os.makedirs(inventory_dir, exist_ok=True)

# 2. Verificar imágenes en el inventario
imagenes = glob.glob(os.path.join(inventory_dir, "*.jpg")) + \
           glob.glob(os.path.join(inventory_dir, "*.jpeg")) + \
           glob.glob(os.path.join(inventory_dir, "*.png"))

print(f"📸 Imágenes de prueba encontradas en el inventario: {len(imagenes)}")
if len(imagenes) > 0:
    for img in imagenes:
        print(f"   -> Detectada: {os.path.basename(img)}")
else:
    print("⚠️ ADVERTENCIA: La carpeta de inventario está vacía. Agrega una foto antes de correr la app.")

# 3. Test de dependencias críticas de imagen
print("\n📦 COMPROBANDO LIBRERÍAS DE PROCESAMIENTO...")
try:
    import google.generativeai as genai
    print("✅ SDK de Google Generative AI cargado correctamente.")
except ImportError:
    print("❌ ERROR: 'google-generativeai' no está instalado.")

try:
    from rembg import remove
    print("✅ Librería de recorte 'rembg' cargada correctamente.")
except ImportError:
    print("❌ ERROR: 'rembg' no está instalado. Ejecuta 'pip install rembg'.")

try:
    import PIL
    print("✅ Librería de imagen 'Pillow' cargada correctamente.")
except ImportError:
    print("❌ ERROR: 'Pillow' no está instalado.")

print("--------------------------------------------------")
print("🏁 DIAGNÓSTICO FINALIZADO. ¡Si todo está en verde, puedes iniciar tu aplicación!")
