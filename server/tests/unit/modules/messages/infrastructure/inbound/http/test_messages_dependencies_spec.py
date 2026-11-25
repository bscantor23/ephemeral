from app.modules.auth.infrastructure.outbound.persistence.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
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
from app.modules.messages.infrastructure.inbound.http.dependencies import (
    get_acknowledge_message_use_case,
    get_message_repository,
    get_pending_messages_use_case,
    get_purge_delivered_messages_use_case,
    get_realtime_notifier,
    get_send_message_use_case,
    get_user_repository,
)
from app.modules.messages.infrastructure.outbound.persistence.repositories.postgres_message_repository import (
    PostgresMessageRepository,
)
from app.modules.messages.infrastructure.outbound.realtime.websocket_realtime_notifier import (
    WebSocketRealtimeNotifier,
)


def test_messages_dependencies():
    """
    ↳ Proveedores de dependencias de mensajes retornan instancias correctas
    """
    repo = get_message_repository()
    assert isinstance(repo, PostgresMessageRepository)

    user_repo = get_user_repository()
    assert isinstance(user_repo, PostgresUserRepository)

    notifier = get_realtime_notifier()
    assert isinstance(notifier, WebSocketRealtimeNotifier)

    send_uc = get_send_message_use_case(
        message_repo=repo, user_repo=user_repo, notifier=notifier
    )
    assert isinstance(send_uc, SendMessageUseCase)

    pending_uc = get_pending_messages_use_case(message_repo=repo)
    assert isinstance(pending_uc, GetPendingMessagesUseCase)

    ack_uc = get_acknowledge_message_use_case(message_repo=repo)
    assert isinstance(ack_uc, AcknowledgeMessageUseCase)

    purge_uc = get_purge_delivered_messages_use_case(message_repo=repo)
    assert isinstance(purge_uc, PurgeDeliveredMessagesUseCase)
