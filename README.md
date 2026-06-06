# Quiniela Live API

API en tiempo real para gestionar quinielas del Mundial 2026. Permite crear quinielas, unir participantes y sortear selecciones en vivo mediante WebSockets.

## Tech Stack

- Django 5.2 + Django REST Framework
- Django Channels (WebSockets con Daphne)
- PostgreSQL (via `dj-database-url`)
- Deploy en Render

## Modelos

- **Seleccion** — 48 selecciones del mundial con fase actual, estado de eliminación y posición final.
- **Quiniela** — Configuración de la quiniela (participantes, premios, slug único).
- **Participante** — Jugador unido a una quiniela con sus selecciones asignadas.

## Endpoints REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/quinielas/` | Listar quinielas |
| POST | `/api/quinielas/` | Crear quiniela |
| GET | `/api/quinielas/{slug}/` | Detalle de quiniela |
| PATCH | `/api/quinielas/{slug}/` | Actualizar quiniela |
| POST | `/api/quinielas/{slug}/unirse/` | Unirse a una quiniela |
| GET | `/api/paises-por-bombo/?participantes=N` | Selecciones agrupadas por bombo |

## WebSocket

Conexión: `ws://<host>/ws/quiniela/{slug}/`

Mensajes del cliente:
- `{"type": "join", "nombre": "..."}` — Unirse a la sala
- `{"type": "start_draw"}` — Iniciar sorteo

Mensajes del servidor:
- `user_list` — Lista actualizada de usuarios conectados
- `draw_started` — Resultados del sorteo con selecciones asignadas
- `error` — Mensaje de error

## Sorteo

Las 48 selecciones se dividen en bombos según el número de participantes (debe ser divisor de 48). De cada bombo se asigna aleatoriamente una selección a cada participante.

## Scripts

```bash
python manage.py runscript crear_paises  # Poblar selecciones
```

## Setup local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runscript crear_paises
daphne quiniela_live_api.asgi:application
```
