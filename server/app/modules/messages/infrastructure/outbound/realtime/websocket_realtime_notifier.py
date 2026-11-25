from uuid import UUID

from app.modules.messages.domain.ports.realtime_notifier_port import (
    RealtimeNotifierPort,
)
from app.modules.messages.domain.value_objects.message_response_vo import (
    MessageResponseVO,
)
from app.modules.messages.infrastructure.inbound.websocket.connection_manager import (
    ConnectionManager,
    global_connection_manager,
)


class WebSocketRealtimeNotifier(RealtimeNotifierPort):
    def __init__(
        self, connection_manager: ConnectionManager = global_connection_manager
    ) -> None:
        self._connection_manager = connection_manager

    async def notify_message(
        self, recipient_id: UUID, message: MessageResponseVO
    ) -> bool:
        payload = {
            "type": "message.incoming",
            "data": {
                "id": str(message.id),
                "chat_session_id": str(message.chat_session_id),
                "sender_id": str(message.sender_id),
                "recipient_id": str(message.recipient_id),
                "protocol_version": message.protocol_version,
                "msg_num": message.msg_num,
                "ciphertext": message.ciphertext,
                "ephemeral_pub": message.ephemeral_pub,
                "signed_prekey_id": (
                    str(message.signed_prekey_id)
                    if message.signed_prekey_id is not None
                    else None
                ),
                "created_at": message.created_at.isoformat(),
            },
        }
        return await self._connection_manager.send_json_to_user(recipient_id, payload)
