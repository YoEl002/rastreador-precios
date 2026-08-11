---

## 📱 Características de la App Android

La aplicación móvil está construida siguiendo las mejores prácticas de desarrollo Android moderno:

* **Lenguaje:** Kotlin
* **Interfaz de Usuario:** Jetpack Compose (Material Design 3 & Modo Oscuro)
* **Arquitectura:** MVVM (Model-View-ViewModel) con `StateFlow` y `Corroutines`
* **Conexión a Red:** OkHttp con técnica de *cache-busting* (`?t=timestamp`) para ignorar la CDN de GitHub Raw y obtener datos frescos.
* **Carga de Imágenes:** Coil para renderizar la gráfica PNG de forma asíncrona.

---

## 🚀 Requisitos para Ejecutar el Script de Python Localmente

Si quieres ejecutar el rastreador en tu equipo:

```bash
# 1. Clonar el repositorio
git clone https://github.com/YoEl002/rastreador-precios.git
cd rastreador-precios

# 2. Instalar dependencias
pip install playwright pandas matplotlib

# 3. Instalar navegadores de Playwright
playwright install chromium

# 4. Ejecutar el rastreador
python rastreador.py
```

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia [MIT](LICENSE).
```
