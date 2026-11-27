from unittest.mock import MagicMock, patch
import pytest
from app.main import create_app, lifespan


@pytest.mark.anyio
async def test_main_create_app():
    """
    ↳ create_app: inicializa la aplicación FastAPI con routers y manejadores
    """
    application = create_app()
    assert application.title == "Ephemeral API"


@pytest.mark.anyio
async def test_main_lifespan_worker_disabled():
    """
    ↳ lifespan: no arranca tarea en segundo plano cuando ENABLE_PURGE_WORKER es False
    """
    app_mock = MagicMock()
    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.ENABLE_PURGE_WORKER = False
        async with lifespan(app_mock):
            pass


@pytest.mark.anyio
async def test_main_lifespan_worker_enabled():
    """
    ↳ lifespan: arranca y cancela limpiamente la tarea de purga cuando ENABLE_PURGE_WORKER es True
    """
    app_mock = MagicMock()
    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.ENABLE_PURGE_WORKER = True
        with patch("app.main.run_periodic_purge") as mock_purge:
            async def _dummy_purge():
                import asyncio
                await asyncio.sleep(10)
            mock_purge.side_effect = _dummy_purge
            async with lifespan(app_mock):
                pass


def test_main_cors_preflight_allowed():
    """
    ↳ create_app: habilita middleware CORS y responde exitosamente a preflight OPTIONS
    """
    from fastapi.testclient import TestClient

    application = create_app()
    client = TestClient(application)

    res = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert res.headers.get("access-control-allow-credentials") == "true"
