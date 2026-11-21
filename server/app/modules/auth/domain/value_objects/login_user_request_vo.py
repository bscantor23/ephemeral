from dataclasses import dataclass


@dataclass(frozen=True)
class LoginUserRequestVO:
    username: str
    password: str
