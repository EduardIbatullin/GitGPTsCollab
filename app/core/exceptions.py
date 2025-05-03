# app/core/exceptions.py

class GitHubAPIError(Exception):
    """
    Базовое исключение для всех ошибок при работе с GitHub API.
    """
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class ResourceNotFoundError(GitHubAPIError):
    """
    Файл или ресурс не найден в репозитории.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class InvalidRepositoryError(GitHubAPIError):
    """
    Репозиторий не найден или имя некорректно.
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=404)
