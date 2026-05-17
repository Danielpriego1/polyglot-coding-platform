# Guía de Despliegue: Plataforma de Codificación Políglota en tu VPS con InsForge

Esta guía te proporcionará los pasos necesarios para desplegar tu plataforma de juego de codificación políglota en un Servidor Privado Virtual (VPS) utilizando Docker e InsForge. Una vez desplegado, el juego podrá funcionar en modo remoto, aprovechando el backend de InsForge para la gestión de niveles, usuarios y la ejecución segura de código.

## 1. Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente:

-   **Un VPS con Ubuntu 22.04 (o similar)**: Acceso SSH con permisos de `sudo`.
-   **Dominio o IP Pública**: La dirección de tu VPS para acceder a la API de InsForge.
-   **Clave API de OpenAI (Opcional)**: Si deseas utilizar el tutor de IA avanzado (GPT-4o), necesitarás una clave `OPENAI_API_KEY`.

## 2. Preparación del VPS

Conéctate a tu VPS vía SSH y sigue estos pasos:

### 2.1. Actualizar el Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2. Instalar Docker y Docker Compose

```bash
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER # Añade tu usuario al grupo docker para no usar sudo
newgrp docker # Aplica los cambios de grupo (puede que necesites reconectar la sesión SSH)
```

## 3. Despliegue de InsForge

Ahora, copia los archivos `docker-compose.yml` y `.env.example` a tu VPS. Puedes usar `scp` o simplemente crear los archivos directamente en el servidor.

### 3.1. Crear Directorio de Proyecto

```bash
mkdir ~/polyglot-platform
cd ~/polyglot-platform
```

### 3.2. Copiar `docker-compose.yml`

Crea un archivo llamado `docker-compose.yml` en `~/polyglot-platform` con el siguiente contenido:

```yaml
version: '3.8'

services:
  insforge-db:
    image: postgres:15-alpine
    container_name: insforge-db
    environment:
      POSTGRES_USER: ${DB_USER:-insforge}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-insforge_pass}
      POSTGRES_DB: ${DB_NAME:-insforge}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - insforge-network

  insforge-api:
    image: insforge/insforge:latest
    container_name: insforge-api
    depends_on:
      - insforge-db
    environment:
      DATABASE_URL: postgresql://${DB_USER:-insforge}:${DB_PASSWORD:-insforge_pass}@insforge-db:5432/${DB_NAME:-insforge}
      JWT_SECRET: ${JWT_SECRET:-super_secret_jwt_key_change_me}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8080:8080"
    networks:
      - insforge-network

  insforge-worker:
    image: insforge/worker:latest
    container_name: insforge-worker
    depends_on:
      - insforge-api
    environment:
      API_URL: http://insforge-api:8080
    networks:
      - insforge-network

networks:
  insforge-network:
    driver: bridge

volumes:
  postgres_data:
```

### 3.3. Configurar el Archivo `.env`

Crea un archivo llamado `.env` en `~/polyglot-platform` (¡no `.env.example`!) y personaliza los valores. **Es crucial cambiar `JWT_SECRET` por una cadena larga y aleatoria.** Si tienes una `OPENAI_API_KEY`, añádela aquí.

```ini
# Configuración de Base de Datos
DB_USER=insforge
DB_PASSWORD=insforge_pass_segura
DB_NAME=insforge_db

# Seguridad
JWT_SECRET=tu_clave_secreta_jwt_muy_larga_y_aleatoria_aqui

# Integraciones de IA (Opcional)
OPENAI_API_KEY=sk-tu_clave_openai_aqui

# Configuración de Red
API_PORT=8080
DB_PORT=5432
```

### 3.4. Iniciar InsForge

Desde el directorio `~/polyglot-platform`, ejecuta:

```bash
docker-compose up -d
```

Esto descargará las imágenes de Docker e iniciará los servicios de InsForge en segundo plano. Puede tardar unos minutos la primera vez.

Verifica que los contenedores estén corriendo:

```bash
docker ps
```

Deberías ver `insforge-db`, `insforge-api` y `insforge-worker` en la lista.

## 4. Despliegue de Edge Functions

Las Edge Functions son el corazón de la ejecución de código remoto. Necesitarás la herramienta `insforge-cli` para desplegarlas. Puedes instalarla en tu máquina local o en el VPS.

### 4.1. Instalar `insforge-cli`

```bash
curl -sSL https://insforge.dev/install.sh | bash
```

### 4.2. Autenticar `insforge-cli`

Necesitarás la URL de tu API de InsForge (ej. `http://tu_ip_o_dominio:8080`) y un token de autenticación. Por ahora, para pruebas, puedes usar un token de administrador que InsForge genera al inicio (consulta los logs del contenedor `insforge-api` si es necesario).

```bash
insforge login --api-url http://tu_ip_o_dominio:8080 --token TU_TOKEN_ADMIN
```

### 4.3. Desplegar las Funciones

Copia los archivos `execute_python.py` y `ai_tutor.py` (y los que crees para JS, Rust, Go, C++) a tu VPS en un directorio (ej. `~/edge_functions`).

```bash
# En tu VPS, dentro de ~/polyglot-platform/edge_functions
# Crea los archivos execute_python.py y ai_tutor.py con el contenido proporcionado anteriormente.

# Despliega la función de Python
insforge function deploy execute_python --file execute_python.py --runtime python3.11

# Despliega la función del Tutor de IA
insforge function deploy ai_tutor --file ai_tutor.py --runtime python3.11

# Repite para JS, Rust, Go, C++ cuando tengas sus Edge Functions
# insforge function deploy execute_javascript --file execute_javascript.js --runtime node18
# insforge function deploy execute_rust --file execute_rust.rs --runtime rust
# ...
```

## 5. Ejecución del Cliente en Modo Remoto

En tu máquina local, donde tienes el archivo `engine.py` de tu juego, puedes ejecutarlo en modo remoto:

```bash
python3 /home/ubuntu/skills/polyglot-coding-game/scripts/engine.py --mode remote --api http://tu_ip_o_dominio:8080
```

Reemplaza `http://tu_ip_o_dominio:8080` con la dirección real de tu InsForge desplegado.

## 6. Próximos Pasos y Desarrollo Futuro

-   **Completar Edge Functions**: Desarrolla las Edge Functions para JavaScript, Rust, Go y C++ siguiendo el mismo patrón que `execute_python.py`.
-   **Integración de Base de Datos**: Modifica `engine.py` para interactuar con la API de InsForge para cargar/guardar niveles y progreso de usuarios.
-   **Interfaz Web**: Considera desarrollar una interfaz web para el juego y el editor de niveles, aprovechando el backend de InsForge.
-   **Monetización**: Implementa las estrategias de monetización descritas en `monetization_roadmap.md`.

¡Con estos pasos, tendrás una base sólida para construir tu plataforma de aprendizaje de programación escalable y monetizable!
