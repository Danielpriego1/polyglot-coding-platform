# 🐍 Polyglot Coding Platform — Play

> Aprende Python (y más lenguajes) jugando. Ejecuta código real en tu navegador sin instalar nada.

## ¿Qué es?

Plataforma gamificada de aprendizaje donde el jugador resuelve retos de código en su navegador usando **Pyodide** (Python WASM), con un motor de laberinto multi-lenguaje y un sistema de puntos y leaderboard.

## Stack

| Capa | Tecnología |
|------|------------|
| Frontend | HTML5 + Vanilla JS + **Pyodide** (Python WASM en browser) |
| Backend | **FastAPI** (Python 3.11) |
| Motor de juego | `engine.py` (laberinto multi-lenguaje: Python, JS, Go, C++, Rust) |
| Deploy | Docker + VPS + Nginx |

## Estructura

```
.
├── engine.py          # Motor laberinto + ejecutores multi-lenguaje
├── main.py            # API FastAPI: retos, progreso, leaderboard
├── index.html         # SPA frontend con editor + Pyodide
├── create_level.py    # Crea niveles JSON
├── levels/            # Niveles del juego (.json)
├── templates/         # Templates de niveles
├── references/        # Referencias de lenguajes
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Deploy rápido (VPS)

```bash
# 1. Clonar
git clone https://github.com/Danielpriego1/polyglot-coding-platform.git
cd polyglot-coding-platform

# 2. Configurar variables
cp .env.example .env
# nano .env → agregar OPENAI_API_KEY si tienes

# 3. Levantar
docker compose up --build -d

# Ver en http://localhost:8000
```

## Nginx + SSL para play.grupopsi.com

```nginx
server {
    listen 80;
    server_name play.grupopsi.com;
    return 301 https://$server_name$request_uri;
}
server {
    listen 443 ssl http2;
    server_name play.grupopsi.com;
    ssl_certificate /etc/letsencrypt/live/play.grupopsi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/play.grupopsi.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }
}
```

```bash
sudo certbot --nginx -d play.grupopsi.com
```

## Features

- ✅ Python real en el navegador via **Pyodide** (sin consumir VPS)
- ✅ 5 retos Python precargados (fácil → difícil)
- ✅ Motor de laberinto multi-lenguaje (Python, JS, Go, C++, Rust)
- ✅ Sistema de puntos y Leaderboard
- ✅ Progreso guardado en localStorage + backend
- ✅ Tutor AI con OpenAI (fallback sin API key)

## Roadmap

- [ ] Conectar PostgreSQL / Supabase para persistencia real
- [ ] Sistema de XP, niveles y logros
- [ ] Modo multijugador
- [ ] Retos de JS, Go, C++
