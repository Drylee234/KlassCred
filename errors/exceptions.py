# errors/exceptions.py

class AppError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class BadRequestError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ForbiddenError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass


class AIServiceError(AppError):
    """Raised when an upstream AI provider (Gemini, Cencori, etc.) fails or
    returns something we can't use — network error, quota exceeded, bad
    response shape, etc. Mapped to 502 (upstream failure), not 500."""
    pass