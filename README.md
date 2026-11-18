# Ephemeral — Mensajería segura extremo a extremo (UD-Chat E2EE)

Proyecto de **Criptografía Aplicada** · Ingeniería en Telemática · Universidad Distrital Francisco José de Caldas.

Sistema de mensajería segura extremo a extremo: el servidor actúa únicamente como directorio de claves públicas y buzón de retransmisión cifrada; toda la criptografía de contenido ocurre en los clientes.

## Estructura del monorepo

```text
ephemeral/
├── server/  # Backend (Arquitectura Hexagonal: Python 3.12 + FastAPI + PostgreSQL 16)
├── client/  # Frontend (Flutter 3: Web + Android)
└── README.md
```
