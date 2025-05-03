# app/core/exceptions.py

class GitHubAPIError(Exception):
    """
    Исключение, возникающее при ошибке взаимодействия с GitHub API.
    Используется для обработки специфических ошибок API.
    """
    pass

class InvalidRepositoryError(Exception):
    """
    Исключение для случая, когда репозиторий не найден или является некорректным.
    """
    pass
