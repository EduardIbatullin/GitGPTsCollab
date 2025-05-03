# app/domain/models.py

from pydantic import BaseModel

class RepoStructureResponse(BaseModel):
    """
    Ответ с информацией о структуре репозитория.

    Attributes:
        repo (str): Имя репозитория.
        tree (list): Список файлов и папок в репозитории.
    """
    repo: str
    tree: list

class FileContentResponse(BaseModel):
    """
    Ответ с содержимым файла в репозитории.

    Attributes:
        path (str): Путь к файлу.
        content (str): Содержимое файла.
        encoding (str): Кодировка файла.
    """
    path: str
    content: str
    encoding: str

class CreateFileRequest(BaseModel):
    """
    Запрос для создания нового файла в репозитории.

    Attributes:
        path (str): Путь к папке в репозитории.
        filename (str): Имя файла.
        content (str): Содержимое файла.
        message (str): Сообщение коммита.
    """
    path: str
    filename: str
    content: str
    message: str

class UpdateFileRequest(BaseModel):
    """
    Запрос для обновления существующего файла в репозитории.

    Attributes:
        path (str): Путь к папке в репозитории.
        filename (str): Имя файла.
        content (str): Новое содержимое файла.
        message (str): Сообщение коммита.
    """
    path: str
    filename: str
    content: str
    message: str

class DeleteFileRequest(BaseModel):
    """
    Запрос для удаления файла из репозитория.

    Attributes:
        path (str): Путь к папке в репозитории.
        filename (str): Имя файла.
        message (str): Сообщение коммита.
    """
    path: str
    filename: str
    message: str
