from typing import Any


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 500,
        details: Any | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            code=f"{resource}_not_found",
            message=f"{resource.capitalize()} not found",
            status_code=404,
            details={"id": identifier},
        )


class RepositoryError(AppError):
    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(
            code="repository_error",
            message=message,
            status_code=500,
            details=details,
        )


class StorageConfigurationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code="storage_configuration_error",
            message=message,
            status_code=500,
        )
