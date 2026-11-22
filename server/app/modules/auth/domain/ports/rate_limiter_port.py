from typing import Protocol


class RateLimiterPort(Protocol):
    def check_and_record(self, key: str) -> None:
        ...

    def reset(self, key: str) -> None:
        ...

