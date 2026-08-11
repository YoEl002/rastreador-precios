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

def obtener_precio_amazon_directo(url, intentos=3):
    print("Abriendo navegador en la nube y buscando el precio...")
    
    for intento in range(1, intentos + 1):
        print(f"Intento {intento} de {intentos}...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--window-size=1920,1080"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="es-ES",
                timezone_id="Europe/Madrid",
                extra_http_headers={
                    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }
            )
            
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            precio_num = None
            
            try:
                # Navegar a la página con margen de tiempo
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(4)

                # Aceptar cookies si aparecen
                if page.locator("#sp-cc-accept").count() > 0:
                    page.locator("#sp-cc-accept").click()
                    time.sleep(1)

                # Selectores prioritarios del precio
                selectores_prioritarios = [
                    "#corePrice_feature_div span.a-offscreen",
                    "#corePriceDisplay_desktop_feature_div span.a-offscreen",
                    "#apex_desktop span.a-offscreen",
                    ".a-box-group span.a-price span.a-offscreen",
                    "span.a-price span.a-offscreen"
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
                                if val > 100:
                                    precio_num = val
                                    break
                        if precio_num:
                            break

            except Exception as e:
                print(f"Error en intento {intento}: {e}")
                
            browser.close()
            
            if precio_num:
                print(f"¡Éxito en el intento {intento}! Precio: {precio_num:.2f}€")
                return precio_num
            
            # Si falla, esperamos 5 segundos antes del siguiente intento
            time.sleep(5)
            
    print("No se pudo obtener el precio tras varios intentos.")
    return None

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
