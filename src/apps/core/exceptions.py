class ApiError(Exception):
    status = 400

    def __init__(self, message: str):
        self.message = message


class NotFoundError(ApiError):
    status = 404


class ForbiddenError(ApiError):
    status = 403


class ConflictError(ApiError):
    status = 409
