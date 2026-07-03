class ResumeIQException(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(ResumeIQException):
    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(f"{resource} with id={resource_id} not found", 404)


class DuplicateException(ResumeIQException):
    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(f"{resource} with {field}='{value}' already exists", 409)


class ValidationException(ResumeIQException):
    def __init__(self, message: str) -> None:
        super().__init__(message, 422)
