import asyncio
from unittest.mock import MagicMock

import pytest

from app.modules.messages.application.ports.purge_delivered_messages_port import (
    PurgeDeliveredMessagesPort,
)
from app.modules.messages.infrastructure.outbound.scheduler.purge_worker import (
    run_periodic_purge,
)


@pytest.mark.anyio
async def test_run_periodic_purge_executes_and_cancels():
    """
    ↳ run_periodic_purge: ejecuta el caso de uso periódicamente y se cancela limpiamente
    """
    mock_use_case = MagicMock(spec=PurgeDeliveredMessagesPort)
    mock_use_case.execute.return_value = 3

    # Ejecuta el worker en segundo plano con intervalo muy corto (0.01s)
    task = asyncio.create_task(
        run_periodic_purge(
            interval_seconds=0.01,
            retention_minutes=10,
            use_case_factory=lambda: mock_use_case,
        )
    )

    await asyncio.sleep(0.035)
    task.cancel()
    await task

    assert mock_use_case.execute.call_count >= 1
    mock_use_case.execute.assert_called_with(10)


@pytest.mark.anyio
async def test_run_periodic_purge_handles_exception_gracefully():
    """
    ↳ run_periodic_purge: captura excepciones durante la ejecución sin abortar el worker
    """
    mock_use_case = MagicMock(spec=PurgeDeliveredMessagesPort)
    mock_use_case.execute.side_effect = [RuntimeError("DB timeout"), 1]

    task = asyncio.create_task(
        run_periodic_purge(
            interval_seconds=0.01,
            retention_minutes=5,
            use_case_factory=lambda: mock_use_case,
        )
    )

    await asyncio.sleep(0.035)
    task.cancel()
    await task

    assert mock_use_case.execute.call_count >= 2
