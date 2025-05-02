
# GitHub Repo Assistant API

Лёгкий FastAPI-сервер для работы с вашими репозиториями на GitHub.  
Позволяет:
- Просмотреть структуру репозитория
- Получить содержимое файла
- Создать новый файл

---

## 📋 Пререквизиты

- Python 3.8+  
- GitHub Personal Access Token с правами «repo»  
- FastAPI и зависимости (см. `requirements.txt`)  

---

## 🚀 Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/your-project.git
   cd your-project
   ```

2. Cоздайте и активируйте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Linux/macOS
   .venv\Scripts\activate          # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Конфигурация

1. Создайте файл `.env` в корне проекта:
   ```dotenv
   GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
   GITHUB_USERNAME=your-github-username
   ```

2. Убедитесь, что в `app/config.py` правильно читаются эти переменные.

---

## ▶️ Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Сервер будет доступен по адресу `http://127.0.0.1:8000`
- Документация Swagger UI: `http://127.0.0.1:8000/docs`

---

## 📮 Эндпоинты

### 1. Получить структуру репозитория

```
GET /repos/{repo}/structure
```

- **Параметры**  
  - `repo` (path) — имя репозитория (например, `my-repo`)

- **Пример**  
  ```bash
  curl http://127.0.0.1:8000/repos/my-repo/structure
  ```

### 2. Получить содержимое файла

```
GET /repos/{repo}/file?path={file_path}
```

- **Параметры**  
  - `repo` (path) — имя репозитория  
  - `path` (query) — путь к файлу внутри репо (например, `src/main.py`)

- **Пример**  
  ```bash
  curl "http://127.0.0.1:8000/repos/my-repo/file?path=README.md"
  ```

### 3. Создать новый файл

```
POST /repos/{repo}/file
Content-Type: application/json
```

- **Параметры**  
  - `repo` (path) — имя репозитория  
  - В теле JSON:
    - `path` — папка внутри репо (без ведущего `/`), например `src`
    - `filename` — имя файла, например `new_script.py`
    - `content` — текст файла
    - `message` — (опционально) сообщение коммита

- **Пример**  
  ```bash
  curl -X POST http://127.0.0.1:8000/repos/my-repo/file \
    -H "Content-Type: application/json" \
    -d '{
      "path": "src",
      "filename": "hello.txt",
      "content": "SGVsbG8sIHdvcmxkIQo=",
      "message": "Add hello.txt"
    }'
  ```

> **Примечание**: в `content` должен быть Base64-закодированный текст (FastAPI-клиент умеет работать с обычным UTF-8 содержимым и сам кодировать).

---

## 📝 Лицензия

Licensed under the MIT License. See [LICENSE](./LICENSE) file for details.

---

© 2025  
