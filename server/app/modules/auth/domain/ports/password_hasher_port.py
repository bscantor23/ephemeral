from typing import Protocol


class PasswordHasherPort(Protocol):
    async def hash_password(self, password: str) -> str:
        ...

    async def verify_password(self, password_hash: str, password: str) -> bool:
        ...

