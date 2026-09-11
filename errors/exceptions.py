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