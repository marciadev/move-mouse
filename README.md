# 🐾 Fluffy Paw Pro

**Fluffy Paw Pro** es una aplicación de automatización tierna y minimalista diseñada para mantener tu sistema activo de una manera divertida. Olvídate de los jigglers de ratón aburridos; deja que un gatito adorable cuide tu escritorio.

![Versión](https://img.shields.io/badge/Versi%C3%B3n-2.0-ff7eb9?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-217346?style=for-the-badge&logo=qt&logoColor=white)

## ✨ Características Principales

<img width="273" height="273" alt="Captura de pantalla 2026-04-16 220710-modified" src="https://github.com/user-attachments/assets/a1b5ce34-8e78-4047-9461-452a8c2c0e47" />

- **Gatito Dinámico**: Reemplaza las imágenes estáticas por una secuencia de videos cortos (.mp4) que rotan cada 5 segundos (Saludando, Jugando, Cazando y Durmiendo).
- **Interfaz "Invisible"**: Los controles se desvanecen suavemente tras 3 segundos de inactividad, dejando solo al gatito en pantalla.
- **Personalización Total**: Cambia el color de acento de la aplicación (Rosa, Azul, Verde, Naranja, Morado o Arcoíris) y todo el panel de ajustes se adaptará.
- **Iconografía Moderna**: Iconos vectoriales SVG nítidos para una estética limpia y delicada.
- **Multitarea Inteligente**: Mantén tu PC activo mediante:
  - Movimiento ligero de la patita (cursor).
  - Simulación de clics.
  - Pulsación de tecla invisible (F15).
- **Modo Pro**: Minimización discreta a la barra de tareas con Tooltip dinámico que indica el estado de la app.

## 🛠️ Tecnologías Utilizadas

- **Python 3**: Lenguaje principal.
- **PySide6 (Qt for Python)**: Framework para la interfaz gráfica avanzada y animaciones.
- **QtMultimedia**: Para la reproducción fluida de clips de video.
- **QtSvg**: Para el renderizado de iconos vectoriales de alta calidad.
- **PyAutoGUI**: Para la simulación segura de entradas de ratón y teclado.
- **JSON**: Gestión persistente de configuraciones de usuario.

## 🚀 Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/fluffy-paw-pro.git
   cd fluffy-paw-pro
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## 🎮 Cómo Funciona

1. **Inicio**: Al abrir la app, el gatito te recibirá con un saludo.
2. **Activación**: Pulsa el botón **Play (▶)** para iniciar el jiggler. El círculo alrededor del gato se llenará indicando el progreso hacia la siguiente acción.
3. **Ajustes**: Pulsa el **Engranaje (⚙️)** para abrir el panel de configuración. Aquí puedes cambiar la frecuencia de movimiento, el tipo de actividad y tu color favorito.
4. **Auto-ocultado**: Mueve el ratón sobre la app para ver los controles; deja de moverlo y desaparecerán en 3 segundos para no estorbar.

## 📂 Requisitos de Archivos

Para que la app funcione con toda su magia, asegúrate de tener estos archivos en la raíz:
- `saludo.mp4`, `jugando.mp4`, `cazando.mp4`, `durmiendo.mp4`: Los videos del gatito.
- `logo.png`: El icono que verás en tu barra de tareas.

---
Hecho con ❤️ y mucha suavidad. ¡Que disfrutes de tu **Fluffy Paw Pro**! 🐾
