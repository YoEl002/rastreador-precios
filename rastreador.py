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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="es-ES"
        )
        page = context.new_page()
        precio_num = None
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(2)
            
            # Botón intermedio si aparece
            boton_seguir = page.get_by_role("button", name=re.compile("Seguir comprando", re.IGNORECASE))
            if boton_seguir.count() > 0:
                boton_seguir.click()
                time.sleep(3)
                if "/dp/" not in page.url:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(3)

            # Aceptar cookies
            if page.locator("#sp-cc-accept").count() > 0:
                page.locator("#sp-cc-accept").click()
                time.sleep(1)

            precio_texto = None
            bloques_mercado = page.locator("#merchantInfoFeature_feature_div")
            total_bloques = bloques_mercado.count()
            
            for i in range(total_bloques):
                texto_bloque = bloques_mercado.nth(i).inner_text()
                if "Amazon" in texto_bloque or "Recíbelo más rápido" in texto_bloque:
                    match = re.search(r'(\d+[\.,]\d{2})\s*€', texto_bloque)
                    if match:
                        precio_texto = match.group(1)
                        break

            if not precio_texto:
                opcion_amazon = page.get_by_role("button", name=re.compile("Recíbelo más rápido", re.IGNORECASE))
                if opcion_amazon.count() > 0:
                    txt = opcion_amazon.first.inner_text()
                    match = re.search(r'(\d+[\.,]\d{2})\s*€', txt)
                    if match:
                        precio_texto = match.group(1)

            if precio_texto:
                limpio = re.sub(r'[^\d,.]', '', precio_texto).replace(',', '.')
                precio_num = float(limpio)
                print(f"¡Éxito! Precio detectado: {precio_num:.2f}€")
            else:
                print("No se pudo aislar el precio.")

        except Exception as e:
            print(f"Error durante la lectura: {e}")
            
        browser.close()
        return precio_num

def registrar_precio(precio):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    precio_formateado = f"{precio:.2f}"
    nuevo_registro = pd.DataFrame([{"Fecha": fecha_actual, "Precio": precio_formateado}])
    
    try:
        df = pd.read_csv(ARCHIVO_CSV)
        df = pd.concat([df, nuevo_registro], ignore_index=True)
    except FileNotFoundError:
        df = nuevo_registro
        
    df.to_csv(ARCHIVO_CSV, index=False)
    print("Historial actualizado en el CSV.")

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
    if precio:
        registrar_precio(precio)
        generar_grafico()
