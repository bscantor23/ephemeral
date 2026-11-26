from app.commons.db.schemas.message_schema import MessageSchema
from app.modules.messages.domain.entities.message_entity import MessageEntity
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.infrastructure.inbound.http.dto.message_response_dto import (
    MessageResponseDTO,
)


class MessageMapper:
    @staticmethod
    def to_entity(schema: MessageSchema) -> MessageEntity:
        return MessageEntity(
            id=schema.id,
            chat_session_id=schema.chat_session_id,
            sender_id=schema.sender_id,
            recipient_id=schema.recipient_id,
            protocol_version=schema.protocol_version,
            msg_num=schema.msg_num,
            ciphertext=schema.ciphertext,
            ephemeral_pub=schema.ephemeral_pub,
            signed_prekey_id=schema.signed_prekey_id,
            delivered_at=schema.delivered_at,
            created_at=schema.created_at,
        )

    @staticmethod
    def to_schema(entity: MessageEntity) -> MessageSchema:
        return MessageSchema(
            id=entity.id,
            chat_session_id=entity.chat_session_id,
            sender_id=entity.sender_id,
            recipient_id=entity.recipient_id,
            protocol_version=entity.protocol_version,
            msg_num=entity.msg_num,
            ciphertext=entity.ciphertext,
            ephemeral_pub=entity.ephemeral_pub,
            signed_prekey_id=entity.signed_prekey_id,
            delivered_at=entity.delivered_at,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_dto(vo: MessageResponseVO) -> MessageResponseDTO:
        return MessageResponseDTO(
            id=vo.id,
            chat_session_id=vo.chat_session_id,
            sender_id=vo.sender_id,
            recipient_id=vo.recipient_id,
            protocol_version=vo.protocol_version,
            msg_num=vo.msg_num,
            ciphertext=vo.ciphertext,
            ephemeral_pub=vo.ephemeral_pub,
            signed_prekey_id=vo.signed_prekey_id,
            delivered_at=vo.delivered_at,
            created_at=vo.created_at,
        )
