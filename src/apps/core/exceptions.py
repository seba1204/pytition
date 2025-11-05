"""Custom exceptions for API errors."""


class ApiError(Exception):
    """Base class for API-related errors."""

    status = 400

    def __init__(self, message: str):
        self.message = message


class NotFoundError(ApiError):
    """Exception for not found errors."""

    status = 404


class ForbiddenError(ApiError):
    """Exception for forbidden access errors."""

    status = 403


class ConflictError(ApiError):
    """Exception for conflict errors."""

    status = 409
