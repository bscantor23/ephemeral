# Ephemeral — Mensajería segura extremo a extremo (UD-Chat E2EE)

Proyecto de **Criptografía Aplicada** · Ingeniería en Telemática · Universidad Distrital Francisco José de Caldas.

Sistema de mensajería segura extremo a extremo: el servidor actúa únicamente como directorio de claves públicas y buzón de retransmisión cifrada; toda la criptografía de contenido ocurre en los clientes.

## Estructura del monorepo

```text
ephemeral/
├── server/  # Backend (Arquitectura Hexagonal: Python 3.12 + FastAPI + PostgreSQL 16 + uv)
├── client/  # Frontend (Flutter 3: Web + Android)
├── docs/    # Documentación y especificaciones
└── README.md
```

## Ejecución del Backend

### Opción 1: Docker Compose (Recomendado)
Levanta la base de datos PostgreSQL y la API aplicando las migraciones automáticamente:

```bash
# 1. Configurar variables de entorno
cp .env.example .env

# 2. Construir y levantar servicios
docker compose up --build
```
La API estará disponible en `http://localhost:8000` con Swagger UI en `http://localhost:8000/docs`.

### Opción 2: Desarrollo Local con uv
Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12.

```bash
cd server

# Sincronizar dependencias exactas con el lockfile
uv sync

# Ejecutar suite de pruebas con cobertura
uv run pytest
```

