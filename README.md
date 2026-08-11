# 📷 Rastreador de Precios Automático - Panasonic LUMIX

Sistema automatizado de monitoreo de precios para la cámara **Panasonic LUMIX** en Amazon España, respaldado por un bot diario en GitHub Actions y visualizado en una aplicación móvil nativa en Android.

---

## 🛠️ ¿Cómo funciona?

1. **Scraping diario (`rastreador.py`):** Un script en Python que utiliza **Playwright** para consultar Amazon.es y extraer el precio actualizado del producto.
2. **Historial y Gráficas:** Los datos recopilados se almacenan en un archivo `historial_precios.csv` y se genera automáticamente una gráfica visual `grafico_precios.png` con **Pandas** y **Matplotlib**.
3. **Automatización con GitHub Actions:** Un flujo de trabajo programado (`ejecutar.yml`) ejecuta el bot todos los días a las 12:00 UTC y guarda los cambios directamente en el repositorio.
4. **App Android (`RastreadorLumix`):** Una aplicación nativa desarrollada en **Kotlin** y **Jetpack Compose** que consume los datos del repositorio en tiempo real para mostrar el último precio y la evolución histórica.

---

## 📊 Arquitectura del Proyecto

```text
[ Amazon.es ] 
     │
     ▼ (Python + Playwright)
[ GitHub Actions (12:00 PM) ] ──► Actualiza CSV y PNG
     │
     ▼ (HTTP / OkHttp con Cache-Busting)
[ App Móvil Android ] 📱 (Jetpack Compose + Coil + MVVM)
📁 Estructura del Repositorio
.github/workflows/ejecutar.yml — Configuración del bot programado (Cron Job) en GitHub Actions.

rastreador.py — Script principal en Python para extraer el precio y generar la gráfica.

historial_precios.csv — Registro histórico acumulado (Fecha, Precio).

grafico_precios.png — Imagen generada de la tendencia de precios.

README.md — Documentación del proyecto.

📱 Características de la App Android
La aplicación móvil está construida siguiendo las mejores prácticas de desarrollo Android moderno:

Lenguaje: Kotlin

Interfaz de Usuario: Jetpack Compose (Material Design 3 & Modo Oscuro)

Arquitectura: MVVM (Model-View-ViewModel) con StateFlow y Corroutines

Conexión a Red: OkHttp con técnica de cache-busting (?t=timestamp) para ignorar la CDN de GitHub Raw y obtener datos frescos.

Carga de Imágenes: Coil para renderizar la gráfica PNG de forma asíncrona.

🚀 Requisitos para Ejecutar el Script de Python Localmente
Si quieres ejecutar el rastreador en tu equipo:

Bash
# 1. Clonar el repositorio
git clone [https://github.com/YoEl002/rastreador-precios.git](https://github.com/YoEl002/rastreador-precios.git)
cd rastreador-precios

# 2. Instalar dependencias
pip install playwright pandas matplotlib

# 3. Instalar navegadores de Playwright
playwright install chromium

# 4. Ejecutar el rastreador
python rastreador.py
📄 Licencia
Este proyecto es de código abierto y está disponible bajo la licencia MIT.


---

¡Y listo! Apaga la pantalla, tómate algo fresco y descansa. Ya tienes el trabajo terminado por hoy. 🚀
