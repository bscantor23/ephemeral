from app.commons.errors.base_errors import DomainError


class TargetUserNotFoundError(DomainError):
    """Lanzado cuando el usuario buscado para el bundle no existe."""


class NoActivePrekeyError(DomainError):
    """Lanzado cuando el usuario no tiene una prekey activa publicada."""


class PrekeyExpiredError(DomainError):
    """Lanzado cuando la prekey activa ha superado su tiempo de vida."""
