import os
import re
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

URL_PRODUCTO = "https://www.amazon.es/dp/B01NCTOKPM"

ARCHIVO_CSV = "historial_precios.csv"
ARCHIVO_GRAFICO = "grafico_precios.png"

# Variables de entorno para Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_notificacion_telegram(mensaje):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, data=payload)
            print("Notificación enviada a Telegram con éxito.")
        except Exception as e:
            print(f"Error al enviar mensaje por Telegram: {e}")

def obtener_precio_amazon_directo(url):
    print("Abriendo navegador en la nube y buscando el precio...")
    with sync_playwright() as p:
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
        
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        precio_num = None
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)

            # Aceptar cookies si aparecen
            if page.locator("#sp-cc-accept").count() > 0:
                page.locator("#sp-cc-accept").click()
                time.sleep(1)

            # Buscar especificamente en la caja de compra principal (Apex / Core Price)
            selectores_prioritarios = [
                "#corePrice_feature_div span.a-offscreen",
                "#corePriceDisplay_desktop_feature_div span.a-offscreen",
                "#apex_desktop span.a-offscreen",
                ".a-box-group span.a-price span.a-offscreen"
            ]

            for selector in selectores_prioritarios:
                elementos = page.locator(selector)
                if elementos.count() > 0:
                    for i in range(elementos.count()):
                        txt = elementos.nth(i).inner_text()
                        match = re.search(r'(\d+[\.,]\d{2})\s*€', txt)
                        if match:
                            precio_texto = match.group(1)
                            limpio = re.sub(r'[^\d,.]', '', precio_texto).replace(',', '.')
                            val = float(limpio)
                            # Si detecta por error el precio sin IVA, le sumamos el IVA o filtramos
                            if val > 100: # Aseguramos que no capture cosas raras
                                precio_num = val
                                print(f"¡Éxito! Precio exacto detectado: {precio_num:.2f}€")
                                break
                    if precio_num:
                        break

            # Si falla la caja principal, usar selector general
            if not precio_num:
                elementos_precio = page.locator("span.a-price span.a-offscreen")
                if elementos_precio.count() > 0:
                    txt = elementos_precio.first.inner_text()
                    match = re.search(r'(\d+[\.,]\d{2})\s*€', txt)
                    if match:
                        precio_texto = match.group(1)
                        limpio = re.sub(r'[^\d,.]', '', precio_texto).replace(',', '.')
                        precio_num = float(limpio)

        except Exception as e:
            print(f"Error durante la lectura: {e}")
            
        browser.close()
        return precio_num

def registrar_precio(precio):
    # Calculamos la hora de España (+2 horas respecto a UTC en horario de verano)
    hora_espana = datetime.utcnow() + timedelta(hours=2)
    fecha_actual = hora_espana.strftime("%Y-%m-%d %H:%M")
    
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
    
    # Respaldo en caso de primera ejecución absoluta si no existe CSV
    if not precio and not os.path.exists(ARCHIVO_CSV):
        print("Creando archivo de inicio predeterminado...")
        precio = 639.10
        
    if precio:
        registrar_precio(precio)
        generar_grafico()
        
        # Enviar notificación de éxito a Telegram
        hora_espana = (datetime.utcnow() + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M")
        mensaje = f"📷 **Rastreador Lumix**\n\nFecha: {hora_espana}\nPrecio detectado: **{precio:.2f} €**"
        enviar_notificacion_telegram(mensaje)
    else:
        # SI FALLA AMAZON, QUE TAMBIÉN TE AVISE POR TELEGRAM Y NO SE QUEDE MUDO
        hora_espana = (datetime.utcnow() + timedelta(hours=2)).strftime("%d/%m/%Y %H:%M")
        mensaje_error = f"⚠️ **Rastreador Lumix**\n\nFecha: {hora_espana}\nNo se ha podido capturar el precio de Amazon en esta ejecución (posible bloqueo temporal)."
        enviar_notificacion_telegram(mensaje_error)
        print("No se pudo obtener el precio de Amazon.")
