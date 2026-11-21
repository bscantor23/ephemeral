from typing import Protocol


class LogoutUserPort(Protocol):
    def execute(self, raw_token: str) -> None:
        ...

