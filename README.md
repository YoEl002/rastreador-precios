📷 Rastreador de Precios Automático - Panasonic LUMIX
Sistema automatizado de monitoreo de precios para una cámara Panasonic LUMIX en Amazon España, respaldado por un bot diario en GitHub Actions y visualizado en una aplicación móvil nativa para Android.
---
🛠️ ¿Cómo funciona?
Scraping diario (`rastreador.py`): Un script en Python que utiliza Playwright para consultar Amazon.es y extraer el precio actualizado del producto.
Historial y gráficas: Los datos recopilados se almacenan en `historial_precios.csv` y se genera automáticamente una gráfica visual `grafico_precios.png` con Pandas y Matplotlib.
Automatización con GitHub Actions: Un flujo de trabajo programado (`ejecutar.yml`) ejecuta el bot todos los días a las 12:00 UTC y guarda los cambios directamente en el repositorio.
App Android (`RastreadorLumix`): Una aplicación nativa desarrollada en Kotlin y Jetpack Compose que consume los datos del repositorio para mostrar el último precio y la evolución histórica.
---
📊 Arquitectura del Proyecto
```text
[ Amazon.es ]
     │
     ▼
[ Python + Playwright ]
     │
     ▼
[ GitHub Actions - 12:00 UTC ]
     │
     ├──► historial_precios.csv
     │
     └──► grafico_precios.png
              │
              ▼
       [ Repositorio GitHub ]
              │
              ▼
       [ App Android ]
```
---
📁 Estructura del Repositorio
```text
rastreador-precios/
│
├── .github/
│   └── workflows/
│       └── ejecutar.yml
│
├── rastreador.py
├── historial_precios.csv
├── grafico_precios.png
└── README.md
```
Archivos principales
`.github/workflows/ejecutar.yml` — Configuración del bot programado mediante GitHub Actions.
`rastreador.py` — Script principal en Python para extraer el precio y generar la gráfica.
`historial_precios.csv` — Registro histórico acumulado con fecha y precio.
`grafico_precios.png` — Imagen generada automáticamente con la evolución del precio.
`README.md` — Documentación del proyecto.
---
📱 Características de la App Android
La aplicación móvil está construida siguiendo las mejores prácticas de desarrollo Android moderno:
Lenguaje: Kotlin
Interfaz de usuario: Jetpack Compose
Diseño: Material Design 3
Tema: Modo oscuro
Arquitectura: MVVM
Gestión de estado: `StateFlow`
Programación asíncrona: Kotlin Coroutines
Conexión a red: OkHttp
Cache-busting: Se añade `?t=timestamp` a las peticiones para evitar contenido almacenado en caché.
Carga de imágenes: Coil para renderizar la gráfica PNG de forma asíncrona.
---
🚀 Requisitos para ejecutar el script de Python localmente
Si quieres ejecutar el rastreador en tu equipo:
1. Clonar el repositorio
```bash
git clone https://github.com/YoEl002/rastreador-precios.git
cd rastreador-precios
```
2. Instalar las dependencias
```bash
pip install playwright pandas matplotlib
```
3. Instalar los navegadores de Playwright
```bash
playwright install chromium
```
4. Ejecutar el rastreador
```bash
python rastreador.py
```
---
⚙️ GitHub Actions
El rastreador se ejecuta automáticamente mediante GitHub Actions.
El flujo de trabajo se encuentra en:
`.github/workflows/ejecutar.yml`
El bot está configurado para ejecutarse diariamente a las 12:00 UTC.
Cuando termina la ejecución, los archivos actualizados se guardan en el repositorio:
`historial_precios.csv`
`grafico_precios.png`
---
📈 Datos generados
El archivo `historial_precios.csv` almacena el histórico de precios.
Ejemplo:
```csv
Fecha,Precio
2026-08-09,899.99
2026-08-10,879.99
2026-08-11,859.99
```
A partir de estos datos se genera automáticamente la gráfica:
`grafico_precios.png`
La gráfica permite visualizar la evolución del precio de la cámara a lo largo del tiempo.
---
🔄 Flujo completo
```text
Amazon.es
    │
    ▼
Python + Playwright
    │
    ▼
rastreador.py
    │
    ├──► Obtiene el precio
    │
    ├──► Actualiza historial_precios.csv
    │
    └──► Genera grafico_precios.png
             │
             ▼
       Repositorio GitHub
             │
             ▼
         App Android
             │
             ├──► OkHttp
             ├──► Cache-Busting
             ├──► Jetpack Compose
             └──► Coil
```
---
📄 Licencia
Este proyecto es de código abierto y está disponible bajo la licencia MIT.
Consulta el archivo `LICENSE` incluido en el repositorio para obtener más información.
---
⚠️ Nota
Este proyecto está destinado a fines educativos y personales.
El funcionamiento del scraping depende de la estructura y disponibilidad de Amazon.es, que puede cambiar en cualquier momento.

