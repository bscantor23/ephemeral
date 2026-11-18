# Ephemeral — Mensajería segura extremo a extremo (UD-Chat E2EE)

Proyecto de **Criptografía Aplicada** · Ingeniería en Telemática · Universidad Distrital Francisco José de Caldas.

Sistema de mensajería segura extremo a extremo (**Alternativa A**): el servidor actúa únicamente como directorio de claves públicas (*prekey bundles*) y buzón de retransmisión cifrada; toda la criptografía de contenido ocurre en los clientes.

## Estructura del monorepo

```text
ephemeral/
├── server/  # Backend (Arquitectura Hexagonal: Python 3.12 + FastAPI + PostgreSQL 16)
├── client/  # Frontend (Flutter 3: Web + Android)
└── README.md
```

## Convenciones de trabajo

- **Ramas:** `main` protegida; desarrollo en ramas `feat/<tema>` y revisión cruzada por PR.
- **Commits:** *Conventional Commits* (`feat:`, `fix:`, `chore:`, `docs:`, `test:`), cada commit desde la cuenta de su autor.
- **Cero secretos:** `.env` fuera del repositorio, validado con `gitleaks`.
