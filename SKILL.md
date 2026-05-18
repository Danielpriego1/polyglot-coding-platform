---
name: polyglot-coding-game
description: Proporciona un juego de codificación basado en terminal para aprender múltiples lenguajes de programación (Python, JavaScript, Rust, Go, C++) con asistencia de IA. Úsalo para crear o jugar desafíos de codificación interactivos en un entorno de terminal.
license: Complete terms in LICENSE.txt
---

# Habilidad: Juego de Codificación Políglota

Esta habilidad permite a los usuarios interactuar con un juego de terminal diseñado para enseñar programación a través de desafíos de laberinto. El jugador controla un personaje (`H`) escribiendo código en varios lenguajes de programación, con el objetivo de alcanzar la salida (`E`).

## Características Principales

-   **Soporte Multilingüe**: Juega y aprende en Python, JavaScript, Rust, Go y C++.
-   **Asistencia de IA**: Un tutor de IA integrado proporciona pistas y consejos educativos cuando el jugador comete errores o necesita ayuda.
-   **Entorno Interactivo**: La interfaz de terminal se actualiza dinámicamente, mostrando el mapa, el inventario y los mensajes del juego.
-   **Niveles Progresivos**: Desafíos diseñados para introducir conceptos de programación de forma gradual.

## Cómo Usar la Habilidad

Para iniciar el juego, ejecuta el script principal:

```bash
python3 /home/ubuntu/skills/polyglot-coding-game/scripts/engine.py
```

El juego te pedirá que elijas un lenguaje de programación (`python`, `javascript`, `rust`, `go`, `cpp`). Una vez seleccionado, podrás introducir comandos para controlar a tu héroe.

### Comandos Básicos del Héroe

El héroe (`hero`) tiene las siguientes acciones disponibles:

-   `move_up()`: Mueve al héroe una casilla hacia arriba.
-   `move_down()`: Mueve al héroe una casilla hacia abajo.
-   `move_left()`: Mueve al héroe una casilla hacia la izquierda.
-   `move_right()`: Mueve al héroe una casilla hacia la derecha.
-   `pick_up_item()`: Recoge un objeto si el héroe está sobre él (por ejemplo, una llave `K`).
-   `use_item()`: Utiliza un objeto del inventario (por ejemplo, para abrir una puerta `D`).

**Nota**: La sintaxis exacta de estos comandos varía ligeramente según el lenguaje. Consulta `/home/ubuntu/skills/polyglot-coding-game/references/languages.md` para ejemplos específicos de cada lenguaje.

### Asistencia de IA

Si te encuentras atascado o cometes un error, el `AITutor` te ofrecerá una pista. Puedes configurar tu `OPENAI_API_KEY` como variable de entorno para habilitar la asistencia de IA avanzada con modelos como GPT-4o. Si no está configurada, el tutor proporcionará consejos predefinidos.

## Estructura de la Habilidad

-   **`SKILL.md`**: Este archivo, que describe la habilidad.
-   **`scripts/engine.py`**: El código fuente principal del juego, incluyendo la lógica del juego, los ejecutores de lenguaje y el tutor de IA.
-   **`references/languages.md`**: Documentación detallada sobre la sintaxis de los comandos para cada lenguaje soportado.
-   **`templates/level_template.json`**: Una plantilla para crear nuevos niveles del juego.

## Creación de Nuevos Niveles

Para añadir nuevos niveles, puedes editar directamente el archivo `scripts/engine.py` y añadir nuevas entradas a la lista `self.levels` en la clase `Game`. Utiliza `templates/level_template.json` como guía para la estructura de cada nivel.