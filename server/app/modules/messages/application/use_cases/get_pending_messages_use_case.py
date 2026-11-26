from uuid import UUID

from app.modules.messages.application.ports.get_pending_messages_port import (
    GetPendingMessagesPort,
)
from app.modules.messages.domain.constants.messages_constants import (
    DEFAULT_PENDING_LIMIT,
)
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.domain.value_objects.pending_messages_response_vo import (
    PendingMessagesResponseVO,
)


class GetPendingMessagesUseCase(GetPendingMessagesPort):
    def __init__(self, message_repository: MessageRepositoryPort) -> None:
        self._message_repository = message_repository

    def execute(
        self, recipient_id: UUID, limit: int = DEFAULT_PENDING_LIMIT
    ) -> PendingMessagesResponseVO:
        safe_limit = limit if limit > 0 else DEFAULT_PENDING_LIMIT
        entities = self._message_repository.get_pending_by_recipient(
            recipient_id, safe_limit
        )

        vos = [
            MessageResponseVO(
                id=e.id,
                chat_session_id=e.chat_session_id,
                sender_id=e.sender_id,
                recipient_id=e.recipient_id,
                protocol_version=e.protocol_version,
                msg_num=e.msg_num,
                ciphertext=e.ciphertext,
                ephemeral_pub=e.ephemeral_pub,
                signed_prekey_id=e.signed_prekey_id,
                delivered_at=e.delivered_at,
                created_at=e.created_at,
            )
            for e in entities
        ]

        return PendingMessagesResponseVO(messages=vos, count=len(vos))
