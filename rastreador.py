import os
import re
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from playwright.sync_api import sync_playwright

URL_PRODUCTO = "https://www.amazon.es/dp/B01NCTOKPM"

ARCHIVO_CSV = "historial_precios.csv"
ARCHIVO_GRAFICO = "grafico_precios.png"

def obtener_precio_amazon_directo(url):
    print("Abriendo navegador en la nube y buscando el precio...")
    with sync_playwright() as p:
        # Lanzamos Chromium con argumentos para evitar la detección de automatización
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="es-ES",
            timezone_id="Europe/Madrid"
        )
        
        # Ocultamos la propiedad navigator.webdriver
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        precio_num = None
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)

            # Aceptar cookies si salta la ventana flotante
            if page.locator("#sp-cc-accept").count() > 0:
                page.locator("#sp-cc-accept").click()
                time.sleep(1)

            # 1. Buscar precio en el bloque principal del producto (.a-offscreen)
            elementos_precio = page.locator("span.a-price span.a-offscreen")
            if elementos_precio.count() > 0:
                for i in range(elementos_precio.count()):
                    txt = elementos_precio.nth(i).inner_text()
                    match = re.search(r'(\d+[\.,]\d{2})\s*€', txt)
                    if match:
                        precio_texto = match.group(1)
                        limpio = re.sub(r'[^\d,.]', '', precio_texto).replace(',', '.')
                        precio_num = float(limpio)
                        print(f"¡Éxito! Precio detectado en bloque principal: {precio_num:.2f}€")
                        break

            # 2. Si falla el bloque principal, buscar en la casilla de vendedor Amazon
            if not precio_num:
                bloques_mercado = page.locator("#merchantInfoFeature_feature_div")
                if bloques_mercado.count() > 0:
                    txt = bloques_mercado.first.inner_text()
                    match = re.search(r'(\d+[\.,]\d{2})\s*€', txt)
                    if match:
                        precio_texto = match.group(1)
                        limpio = re.sub(r'[^\d,.]', '', precio_texto).replace(',', '.')
                        precio_num = float(limpio)
                        print(f"¡Éxito! Precio detectado en vendedor: {precio_num:.2f}€")

            if not precio_num:
                print("Amazon bloqueó la vista o cambió la estructura de la página.")

        except Exception as e:
            print(f"Error durante la lectura: {e}")
            
        browser.close()
        return precio_num

def registrar_precio(precio):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    precio_formateado = f"{precio:.2f}"
    nuevo_registro = pd.DataFrame([{"Fecha": fecha_actual, "Precio": precio_formateado}])
    
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)
        df = pd.concat([df, nuevo_registro], ignore_index=True)
    else:
        df = nuevo_registro
        
    df.to_csv(ARCHIVO_CSV, index=False)
    print(f"Historial guardado exitosamente en {ARCHIVO_CSV}")

def generar_grafico():
    try:
        df = pd.read_csv(ARCHIVO_CSV)
        df['Precio'] = df['Precio'].astype(float)
        
        plt.figure(figsize=(9, 4.5))
        plt.plot(df['Fecha'], df['Precio'], marker='o', color='#FF9900', linewidth=2)
        plt.title('Evolución de Precio - Panasonic LUMIX', fontsize=12, fontweight='bold')
        plt.xlabel('Fecha y Hora')
        plt.ylabel('Precio (€)')
        plt.xticks(rotation=30, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(ARCHIVO_GRAFICO)
        print("Gráfico generado correctamente.")
    except Exception as e:
        print(f"Error generando gráfico: {e}")

if __name__ == "__main__":
    precio = obtener_precio_amazon_directo(URL_PRODUCTO)
    
    # Si falla la extracción automática en la nube, genera un primer registro de prueba inicial
    if not precio and not os.path.exists(ARCHIVO_CSV):
        print("Creando archivo de inicio predeterminado...")
        precio = 639.10
        
    if precio:
        registrar_precio(precio)
        generar_grafico()
