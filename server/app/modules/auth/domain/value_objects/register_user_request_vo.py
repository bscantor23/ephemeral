from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserRequestVO:
    username: str
    display_name: str
    password: str
    identity_sign_pub: str
    identity_dh_pub: str
    identity_dh_sig: str
