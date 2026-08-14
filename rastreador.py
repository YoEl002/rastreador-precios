import os
import re
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from zoneinfo import ZoneInfo
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
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="es-ES",
                timezone_id="Europe/Madrid",
                permissions=["geolocation"]
            )
            
            page = context.new_page()
            precio_num = None
            
            try:
                url_limpia = f"https://www.amazon.es/dp/B01NCTOKPM?th=1&psc=1"
                page.goto(url_limpia, wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)

                # 1. Extraer desde JSON-LD
                scripts_json = page.locator('script[type="application/ld+json"]').all()
                for script in scripts_json:
                    try:
                        contenido = script.inner_text()
                        import json
                        datos = json.loads(contenido)
                        if isinstance(datos, dict) and "offers" in datos:
                            offers = datos["offers"]
                            if isinstance(offers, list) and len(offers) > 0:
                                val = float(offers[0].get("price", 0))
                            elif isinstance(offers, dict):
                                val = float(offers.get("price", 0))
                            
                            if val > 100:
                                precio_num = round(val * 1.21, 2)
                                print(f"¡Éxito desde JSON-LD! Precio: {precio_num:.2f}€")
                                break
                    except Exception:
                        continue

                # 2. Respaldo por selectores si no se obtuvo por JSON
                if not precio_num:
                    selectores = [
                        "span.a-price span.a-offscreen",
                        "#corePrice_feature_div span.a-offscreen",
                        ".apexPriceToPay span.a-offscreen"
                    ]
                    for selector in selectores:
                        elem = page.locator(selector)
                        if elem.count() > 0:
                            txt = elem.first.inner_text()
                            match = re.search(r'(\d+[\.,]\d{2})', txt)
                            if match:
                                val = float(match.group(1).replace(',', '.'))
                                if val > 100:
                                    precio_num = round(val * 1.21, 2)
                                    break

            except Exception as e:
                print(f"Error en intento {intento}: {e}")
                
            browser.close()
            
            if precio_num:
                return precio_num
            
            time.sleep(4)
            
    # Plan de Respaldo CSV
    if os.path.exists(ARCHIVO_CSV):
        try:
            df = pd.read_csv(ARCHIVO_CSV)
            if not df.empty:
                ultimo_precio = float(df['Precio'].iloc[-1])
                print(f"Usando precio de respaldo del CSV.")
                return ultimo_precio
        except Exception as e:
            print(f"Error al leer respaldo: {e}")

    return None

def registrar_precio(precio):
    zona_madrid = ZoneInfo("Europe/Madrid")
    ahora_espana = datetime.now(zona_madrid)
    fecha_actual = ahora_espana.strftime("%Y-%m-%d %H:%M")
    
    precio_formateado = f"{precio:.2f}"
    nuevo_registro = pd.DataFrame([{
        "Fecha": fecha_actual, 
        "Precio": precio_formateado
    }])
    
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
        plt.title('Evolución de Precio - Panasonic LUMIX 100-300mm', fontsize=12, fontweight='bold')
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
    
    if not precio and not os.path.exists(ARCHIVO_CSV):
        print("Creando archivo de inicio predeterminado...")
        precio = 639.10
        
    if precio:
        if os.path.exists(ARCHIVO_CSV):
            try:
                df_previo = pd.read_csv(ARCHIVO_CSV)
                if not df_previo.empty:
                    ultimo_precio_registrado = float(df_previo['Precio'].iloc[-1])
                    if precio < (ultimo_precio_registrado - 50):
                        alerta_brusca = f"🚨 **¡CHOLLO / BAJADA BRUSCA DE PRECIO!** 🚨\n\nEl precio ha caído de **{ultimo_precio_registrado:.2f} €** a **{precio:.2f} €**"
                        enviar_notificacion_telegram(alerta_brusca)
            except Exception as e:
                print(f"Error comprobando bajada brusca: {e}")

        registrar_precio(precio)
        generar_grafico()
        
        zona_madrid = ZoneInfo("Europe/Madrid")
        hora_espana_str = datetime.now(zona_madrid).strftime("%d/%m/%Y %H:%M")
        mensaje = f"📷 **Lumix Tracker**\n\nFecha: {hora_espana_str}\nPrecio detectado: **{precio:.2f} €**"
        enviar_notificacion_telegram(mensaje)
    else:
        zona_madrid = ZoneInfo("Europe/Madrid")
        hora_espana_str = datetime.now(zona_madrid).strftime("%d/%m/%Y %H:%M")
        mensaje_error = f"⚠️ **Lumix Tracker**\n\nFecha: {hora_espana_str}\nNo se ha podido capturar el precio de Amazon en esta ejecución."
        enviar_notificacion_telegram(mensaje_error)
        print("No se pudo obtener el precio de Amazon.")
