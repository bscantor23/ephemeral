from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from app.modules.auth.domain.value_objects.user_response_vo import UserResponseVO
from app.modules.auth.infrastructure.outbound.security.auth_security import (
    get_current_user,
)
from app.modules.messages.application.ports.acknowledge_message_port import (
    AcknowledgeMessagePort,
)
from app.modules.messages.application.ports.get_pending_messages_port import (
    GetPendingMessagesPort,
)
from app.modules.messages.application.ports.send_message_port import SendMessagePort
from app.modules.messages.domain.constants.messages_constants import (
    DEFAULT_PENDING_LIMIT,
)
from app.modules.messages.domain.value_objects.send_message_request_vo import (
    SendMessageRequestVO,
)
from app.modules.messages.infrastructure.inbound.http.dependencies import (
    get_acknowledge_message_use_case,
    get_pending_messages_use_case,
    get_send_message_use_case,
)
from app.modules.messages.infrastructure.inbound.http.dto.message_response_dto import (
    MessageResponseDTO,
    PendingMessagesResponseDTO,
)
from app.modules.messages.infrastructure.inbound.http.dto.send_message_dto import (
    SendMessageRequestDTO,
)
from app.modules.messages.infrastructure.outbound.persistence.mappers.message_mapper import (
    MessageMapper,
)

router = APIRouter(tags=["Messages"])


@router.post(
    "",
    response_model=MessageResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje cifrado",
)
async def send_message(
    payload: SendMessageRequestDTO,
    current_user: UserResponseVO = Depends(get_current_user),
    use_case: SendMessagePort = Depends(get_send_message_use_case),
) -> MessageResponseDTO:
    vo = SendMessageRequestVO(
        recipient_id=payload.recipient_id,
        chat_session_id=payload.chat_session_id,
        msg_num=payload.msg_num,
        ciphertext=payload.ciphertext,
        ephemeral_pub=payload.ephemeral_pub,
        signed_prekey_id=payload.signed_prekey_id,
        protocol_version=payload.protocol_version,
    )
    result = await use_case.execute(sender_id=current_user.id, request=vo)
    return MessageMapper.to_dto(result)


@router.get(
    "/pending",
    response_model=PendingMessagesResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Recuperar mensajes diferidos pendientes",
)
def get_pending_messages(
    limit: int = Query(default=DEFAULT_PENDING_LIMIT, ge=1, le=500),
    current_user: UserResponseVO = Depends(get_current_user),
    use_case: GetPendingMessagesPort = Depends(get_pending_messages_use_case),
) -> PendingMessagesResponseDTO:
    result = use_case.execute(recipient_id=current_user.id, limit=limit)
    return PendingMessagesResponseDTO(
        messages=[MessageMapper.to_dto(m) for m in result.messages],
        count=result.count,
    )


@router.post(
    "/{message_id}/ack",
    response_model=MessageResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Confirmar acuse de recibo de entrega",
)
def acknowledge_message(
    message_id: UUID,
    current_user: UserResponseVO = Depends(get_current_user),
    use_case: AcknowledgeMessagePort = Depends(get_acknowledge_message_use_case),
) -> MessageResponseDTO:
    result = use_case.execute(current_user_id=current_user.id, message_id=message_id)
    return MessageMapper.to_dto(result)
