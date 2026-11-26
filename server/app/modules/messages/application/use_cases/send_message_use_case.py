from uuid import UUID

from app.modules.auth.domain.ports.user_repository_port import UserRepositoryPort
from app.modules.messages.application.ports.send_message_port import SendMessagePort
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.domain.errors.messages_errors import RecipientNotFoundError
from app.modules.messages.domain.ports.message_repository_port import (
    MessageRepositoryPort,
)
from app.modules.messages.domain.ports.realtime_notifier_port import (
    RealtimeNotifierPort,
)
from app.modules.messages.domain.rules.messages_rules import MessagesRules
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.domain.value_objects.send_message_request_vo import (
    SendMessageRequestVO,
)


class SendMessageUseCase(SendMessagePort):
    def __init__(
        self,
        message_repository: MessageRepositoryPort,
        user_repository: UserRepositoryPort,
        realtime_notifier: RealtimeNotifierPort,
    ) -> None:
        self._message_repository = message_repository
        self._user_repository = user_repository
        self._realtime_notifier = realtime_notifier

    async def execute(
        self, sender_id: UUID, request: SendMessageRequestVO
    ) -> MessageResponseVO:
        MessagesRules.validate_parties(sender_id, request.recipient_id)
        MessagesRules.validate_message_payload(
            msg_num=request.msg_num,
            ciphertext=request.ciphertext,
            protocol_version=request.protocol_version,
        )

        recipient = self._user_repository.get_by_id(request.recipient_id)
        if recipient is None:
            raise RecipientNotFoundError()

        entity = MessageEntity.create(
            chat_session_id=request.chat_session_id,
            sender_id=sender_id,
            recipient_id=request.recipient_id,
            protocol_version=request.protocol_version,
            msg_num=request.msg_num,
            ciphertext=request.ciphertext,
            ephemeral_pub=request.ephemeral_pub,
            signed_prekey_id=request.signed_prekey_id,
        )

        saved = self._message_repository.save(entity)

        response_vo = MessageResponseVO(
            id=saved.id,
            chat_session_id=saved.chat_session_id,
            sender_id=saved.sender_id,
            recipient_id=saved.recipient_id,
            protocol_version=saved.protocol_version,
            msg_num=saved.msg_num,
            ciphertext=saved.ciphertext,
            ephemeral_pub=saved.ephemeral_pub,
            signed_prekey_id=saved.signed_prekey_id,
            delivered_at=saved.delivered_at,
            created_at=saved.created_at,
        )

        await self._realtime_notifier.notify_message(request.recipient_id, response_vo)

        return response_vo
