# GitHub Repo Assistant API

Лёгкий FastAPI-сервер для работы с вашими репозиториями на GitHub.  
Позволяет:
- Просмотреть структуру репозитория  
- Получить содержимое файла  
- Создать новый файл  

---

## 📋 Пререквизиты

- Python 3.8+  
- GitHub Personal Access Token с правами `repo`  
- Зависимости (см. `requirements.txt` и `requirements-dev.txt`)  

---

## 🚀 Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/your-project.git
   cd your-project
````

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Linux/macOS
   .venv\Scripts\activate          # Windows
   ```

3. Установите основные зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. (Опционально) Установите dev-зависимости:

   ```bash
   pip install -r requirements-dev.txt
   ```

---

## 🔧 Конфигурация

1. Создайте файл `.env` в корне проекта:

   ```dotenv
   MY_GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
   MY_GITHUB_USERNAME=your-github-username
   ```

2. Проверьте, что `app/core/config.py` читает именно эти переменные:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   MY_GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
   MY_GITHUB_USERNAME = os.getenv("MY_GITHUB_USERNAME")
   ```

---

## ▶️ Запуск сервера

```bash
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

* Сервер будет доступен по адресу `http://127.0.0.1:8000`
* Swagger UI: `http://127.0.0.1:8000/docs`

---

## 📮 Эндпоинты

### 1. Получить структуру репозитория

```
GET /repos/{repo}/structure
```

* **Path**

  * `repo` — имя репозитория, например `my-repo`

* **Пример**

  ```bash
  curl http://127.0.0.1:8000/repos/my-repo/structure
  ```

* **Ответ**

  ```json
  {
    "repo": "my-repo",
    "tree": [
      { "path": "", "type": "dir" },
      { "path": "README.md", "type": "file" },
      { "path": "src", "type": "dir" }
    ]
  }
  ```

---

### 2. Получить содержимое файла

```
GET /repos/{repo}/file?path={file_path}
```

* **Path**

  * `repo` — имя репозитория

* **Query**

  * `path` — путь к файлу внутри репозитория, например `README.md` или `src/main.py`

* **Пример**

  ```bash
  curl "http://127.0.0.1:8000/repos/my-repo/file?path=README.md"
  ```

* **Ответ**

  ```json
  {
    "path": "README.md",
    "content": "Artem Shumeyko's course \"FastAPI — immersion in backend development in Python\"",
    "encoding": "utf-8"
  }
  ```

---

### 3. Создать новый файл

```
POST /repos/{repo}/file
Content-Type: application/json
```

* **Path**

  * `repo` — имя репозитория

* **Body** (JSON)

  * `path` — папка внутри репозитория без ведущего `/`; пустая строка или отсутствие поля = корень
  * `filename` — имя нового файла, например `hello.txt`
  * `content` — текст файла в UTF-8 (не Base64)
  * `message` — сообщение коммита (по умолчанию `"Create file via API"`)

* **Примеры**

  **а) В корень репозитория**

  ```bash
  curl -X POST http://127.0.0.1:8000/repos/my-repo/file \
    -H "Content-Type: application/json" \
    -d '{
      "filename": "hello.txt",
      "content": "Привет, мир!",
      "message": "Add hello.txt"
    }'
  ```

  **б) В папку `src/`**

  ```bash
  curl -X POST http://127.0.0.1:8000/repos/my-repo/file \
    -H "Content-Type: application/json" \
    -d '{
      "path": "src",
      "filename": "utils.py",
      "content": "print(\"Hello from utils\")",
      "message": "Add utils.py"
    }'
  ```

* **Ответ**

  ```json
  {
    "path": "hello.txt",
    "content": "Привет, мир!",
    "encoding": "utf-8"
  }
  ```

---

## 📝 Лицензия

Licensed under the MIT License. See [LICENSE](./LICENSE) for details.

© 2025
