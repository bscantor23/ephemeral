from datetime import datetime, timezone
from uuid import UUID

from app.modules.messages.application.ports.acknowledge_message_port import (
    AcknowledgeMessagePort,
)
from app.modules.messages.domain.errors.messages_errors import MessageNotFoundError
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)
from app.modules.messages.domain.rules.messages_rules import MessagesRules
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)


class AcknowledgeMessageUseCase(AcknowledgeMessagePort):
    def __init__(self, message_repository: MessageRepositoryPort) -> None:
        self._message_repository = message_repository

    def execute(self, current_user_id: UUID, message_id: UUID) -> MessageResponseVO:
        message = self._message_repository.get_by_id(message_id)
        if message is None:
            raise MessageNotFoundError()

        MessagesRules.validate_ack_authorization(
            message_recipient_id=message.recipient_id,
            current_user_id=current_user_id,
        )

        if message.delivered_at is not None:
            return MessageResponseVO(
                id=message.id,
                chat_session_id=message.chat_session_id,
                sender_id=message.sender_id,
                recipient_id=message.recipient_id,
                protocol_version=message.protocol_version,
                msg_num=message.msg_num,
                ciphertext=message.ciphertext,
                ephemeral_pub=message.ephemeral_pub,
                signed_prekey_id=message.signed_prekey_id,
                delivered_at=message.delivered_at,
                created_at=message.created_at,
            )

        now = datetime.now(timezone.utc)
        updated = self._message_repository.mark_delivered(message_id, now)

        result = updated if updated is not None else message.mark_delivered(now)

        return MessageResponseVO(
            id=result.id,
            chat_session_id=result.chat_session_id,
            sender_id=result.sender_id,
            recipient_id=result.recipient_id,
            protocol_version=result.protocol_version,
            msg_num=result.msg_num,
            ciphertext=result.ciphertext,
            ephemeral_pub=result.ephemeral_pub,
            signed_prekey_id=result.signed_prekey_id,
            delivered_at=result.delivered_at,
            created_at=result.created_at,
        )
