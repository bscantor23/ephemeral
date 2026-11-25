import asyncio
import logging
from typing import Callable, Optional

from app.commons.config.settings import get_settings
from app.modules.messages.application.ports.purge_delivered_messages_port import (
    PurgeDeliveredMessagesPort,
)
from app.modules.messages.infrastructure.inbound.http.dependencies import (
    get_purge_delivered_messages_use_case,
)

logger = logging.getLogger(__name__)


async def run_periodic_purge(
    interval_seconds: Optional[int] = None,
    retention_minutes: Optional[int] = None,
    use_case_factory: Optional[Callable[[], PurgeDeliveredMessagesPort]] = None,
) -> None:
    settings = get_settings()
    interval = interval_seconds or settings.PURGE_INTERVAL_SECONDS
    retention = retention_minutes or settings.MESSAGE_RETENTION_MINUTES
    factory = use_case_factory or get_purge_delivered_messages_use_case

    logger.info(
        f"Iniciando tarea periódica de purga de mensajes efímeros: cada {interval}s, retención {retention}min"
    )

    try:
        while True:
            await asyncio.sleep(interval)
            try:
                use_case = factory()
                deleted_count = use_case.execute(retention)
                if deleted_count > 0:
                    logger.info(
                        f"Purga de mensajes completada: {deleted_count} mensaje(s) eliminados."
                    )
            except Exception as e:
                logger.error(f"Error durante la purga periódica de mensajes: {e}")
    except asyncio.CancelledError:
        logger.info("Tarea periódica de purga de mensajes cancelada.")
