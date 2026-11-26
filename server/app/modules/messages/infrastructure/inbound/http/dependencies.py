from fastapi import Depends

from app.commons.config.settings import get_settings
from app.modules.auth.domain.ports.user_repository_port import UserRepositoryPort
from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.modules.messages.application.ports.acknowledge_message_port import (
    AcknowledgeMessagePort,
)
from app.modules.messages.application.ports.get_pending_messages_port import (
    GetPendingMessagesPort,
)
from app.modules.messages.application.ports.purge_delivered_messages_port import (
    PurgeDeliveredMessagesPort,
)
from app.modules.messages.application.ports.send_message_port import SendMessagePort
from app.modules.messages.application.use_cases.acknowledge_message_use_case import (
    AcknowledgeMessageUseCase,
)
from app.modules.messages.application.use_cases.get_pending_messages_use_case import (
    GetPendingMessagesUseCase,
)
from app.modules.messages.application.use_cases.purge_delivered_messages_use_case import (
    PurgeDeliveredMessagesUseCase,
)
from app.modules.messages.application.use_cases.send_message_use_case import (
    SendMessageUseCase,
)
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)
from app.modules.messages.domain.ports.realtime_notifier_port import (
    RealtimeNotifierPort,
)
from app.modules.messages.infrastructure.outbound.persistence.repositories.postgres_message_repository import (
    PostgresMessageRepository,
)
from app.modules.messages.infrastructure.outbound.realtime.websocket_realtime_notifier import (
    WebSocketRealtimeNotifier,
)


def get_message_repository() -> MessageRepositoryPort:
    return PostgresMessageRepository()


def get_user_repository() -> UserRepositoryPort:
    return PostgresUserRepository()


def get_realtime_notifier() -> RealtimeNotifierPort:
    return WebSocketRealtimeNotifier()


def get_send_message_use_case(
    message_repo: MessageRepositoryPort = Depends(get_message_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    notifier: RealtimeNotifierPort = Depends(get_realtime_notifier),
) -> SendMessagePort:
    return SendMessageUseCase(
        message_repository=message_repo,
        user_repository=user_repo,
        realtime_notifier=notifier,
    )


def get_pending_messages_use_case(
    message_repo: MessageRepositoryPort = Depends(get_message_repository),
) -> GetPendingMessagesPort:
    return GetPendingMessagesUseCase(message_repository=message_repo)


def get_acknowledge_message_use_case(
    message_repo: MessageRepositoryPort = Depends(get_message_repository),
) -> AcknowledgeMessagePort:
    return AcknowledgeMessageUseCase(message_repository=message_repo)


def get_purge_delivered_messages_use_case(
    message_repo: MessageRepositoryPort = Depends(get_message_repository),
) -> PurgeDeliveredMessagesPort:
    settings = get_settings()
    return PurgeDeliveredMessagesUseCase(
        message_repo=message_repo,
        default_retention_minutes=settings.MESSAGE_RETENTION_MINUTES,
    )
