from uuid import UUID

from app.modules.messages.domain.constants.messages_constants import (
    MAX_CIPHERTEXT_LENGTH,
    MIN_CIPHERTEXT_LENGTH,
    MIN_MSG_NUM,
)
from app.modules.messages.domain.errors.messages_errors import (
    InvalidMessagePayloadError,
    SelfMessageNotAllowedError,
    UnauthorizedMessageAckError,
)


class MessagesRules:
    @staticmethod
    def validate_parties(sender_id: UUID, recipient_id: UUID) -> None:
        if sender_id == recipient_id:
            raise SelfMessageNotAllowedError()

    @staticmethod
    def validate_message_payload(
        msg_num: int, ciphertext: str, protocol_version: int
    ) -> None:
        if msg_num < MIN_MSG_NUM:
            raise InvalidMessagePayloadError("Message number cannot be negative")

        cleaned = ciphertext.strip() if ciphertext else ""
        if (
            len(cleaned) < MIN_CIPHERTEXT_LENGTH
            or len(cleaned) > MAX_CIPHERTEXT_LENGTH
        ):
            raise InvalidMessagePayloadError(
                f"Ciphertext length must be between {MIN_CIPHERTEXT_LENGTH} and {MAX_CIPHERTEXT_LENGTH} bytes"
            )

        if protocol_version < 1:
            raise InvalidMessagePayloadError("Protocol version must be greater than or equal to 1")

    @staticmethod
    def validate_ack_authorization(
        message_recipient_id: UUID, current_user_id: UUID
    ) -> None:
        if message_recipient_id != current_user_id:
            raise UnauthorizedMessageAckError()
