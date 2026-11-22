from dataclasses import dataclass


@dataclass(frozen=True)
class UploadPrekeyRequestVO:
    signed_prekey_pub: str
    signature: str
