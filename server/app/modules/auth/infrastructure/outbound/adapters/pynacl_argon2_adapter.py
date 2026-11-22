import asyncio
import nacl.exceptions
import nacl.pwhash.argon2id

from app.modules.auth.domain.constants.auth_constants import (
    ARGON2_MEMLIMIT,
    ARGON2_OPSLIMIT,
)
from app.modules.auth.domain.ports.password_hasher_port import (
    PasswordHasherPort,
)


class PyNaClArgon2Adapter(PasswordHasherPort):
    def __init__(self, max_concurrency: int = 4) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def hash_password(self, password: str) -> str:
        async with self._semaphore:
            raw_hash = await asyncio.to_thread(
                nacl.pwhash.argon2id.str,
                password.encode("utf-8"),
                opslimit=ARGON2_OPSLIMIT,
                memlimit=ARGON2_MEMLIMIT,
            )
            return raw_hash.decode("utf-8")

    async def verify_password(self, password_hash: str, password: str) -> bool:
        async with self._semaphore:
            def _verify() -> bool:
                try:
                    return nacl.pwhash.argon2id.verify(
                        password_hash.encode("utf-8"),
                        password.encode("utf-8"),
                    )
                except nacl.exceptions.CryptoError:
                    return False

            return await asyncio.to_thread(_verify)
