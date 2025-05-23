# 🏃 Server-side OptiMasFit

## **Бэкенд-часть дипломного проекта OptiMasFit**

## 📑 Содержание

1. 📝 Описание проекта
2. 🛠️ Технический стек
3. 📂 Структура репозитория
4. 🚀 Установка
5. ⚙️ Конфигурация
6. ▶️ Запуск приложения
7. 🗄️ База данных и миграции
8. 🌐 API и маршруты
9. 🔄 CI/CD

---

## 📝 Описание проекта

Серверная часть OptiMasFit отвечает за хранение, обработку и передачу данных о пользователях, их тренировках и рекомендациях. Сервис обеспечивает:

* Аутентификация и авторизация через DRF-токены
* CRUD-операции над пользователями и рекомендациями
* Генерацию и валидацию схемы OpenAPI (Swagger)

## 🛠️ Технический стек

* **Язык:** Python
* **Фреймворк:** Django, Django REST Framework
* **База данных:** PostgreSQL
* **CI/CD:** GitHub Actions
* **Линтинг:** flake8

## 📂 Структура репозитория

```text
└─optimas-backend/
   ├── .github/                   # CI/CD workflow
   │   └── workflows/ci.yml       # GitHub Actions
   ├── optimassfit/               # Django-проект
   │   ├── users/                 # Приложение users
   │   │   ├── migrations/        # Файлы миграций БД
   │   │   ├── admin.py           # Регистрация моделей в Django Admin
   │   │   ├── api_urls.py        # Маршруты JSON-API для DRF
   │   │   ├── api_views.py       # ViewSet’ы и API-контроллеры
   │   │   ├── apps.py            # Конфигурация приложения users
   │   │   ├── models.py          # Описание моделей данных (User, Profile, Recommendation)
   │   │   ├── serializers.py     # Сериализация: модели ↔ JSON (валидация входных данных)
   │   │   └── utils.py           # Утилиты: вспомогательные функции и генерация рекомендаций
   │   ├── asgi.py                # ASGI-конфиг для async-запросов
   │   ├── settings.py            # Конфигурация проекта
   │   ├── urls.py                # Основные маршруты
   │   └── wsgi.py                # WSGI-конфиг для деплоя
   ├── manage.py                  # Скрипт управления Django
   ├── requirements.txt           # Список зависимостей
   └── README.md                  # Текущее руководство
```

## 🚀 Установка

1. **Клонировать репозиторий**

   ```bash
   git clone https://github.com/Quant60/optimas-backend.git
   cd optimas-backend
   ```
2. **Создать виртуальное окружение и активировать его**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/macOS
   .\.venv\Scripts\activate     # Windows
   ```
3. **Установить зависимости**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## ⚙️ Конфигурация

Проект читает настройки из переменных окружения:

| Переменная          | Описание                                                 |
| ------------------- | -------------------------------------------------------- |
| `POSTGRES_DB`       | Имя базы данных PostgreSQL (по умолчанию `test_db` в CI) |
| `POSTGRES_USER`     | Пользователь БД (по умолчанию `postgres`)                |
| `POSTGRES_PASSWORD` | Пароль к БД (по умолчанию `postgres`)                    |
| `POSTGRES_HOST`     | Хост БД (по умолчанию `localhost`)                       |
| `POSTGRES_PORT`     | Порт БД (по умолчанию `5432`)                            |
| `DJANGO_SECRET_KEY` | Секретный ключ Django                                    |
| `DATABASE_URL`      | Альтернативная строка подключения к БД                   |

Можно использовать файл `.env` и пакет `django-environ` или `python-dotenv`.

## ▶️ Запуск приложения

```bash
python manage.py migrate --fake-initial  # Применить миграции
python manage.py runserver              # Запустить сервер на http://127.0.0.1:8000
```

## 🗄️ База данных и миграции

* Миграции находятся в `optimassfit/users/migrations`.
* Для корректного CI применяйте флаг `--fake-initial`.

## 🌐 API и маршруты

### Web UI

* `GET /users/` — список пользователей
* `POST /users/` — создать пользователя

### JSON API

* `GET /api/users/` — получить список пользователей
* `POST /api/users/` — создать пользователя

Для полного списка эндпоинтов см. `optimassfit/users/api_urls.py`.

### Документация OpenAPI

```bash
python manage.py spectacular --serve
```

Открыть в браузере: `http://127.0.0.1:8000/schema/`

## 🔄 CI/CD

Настроен GitHub Actions (`.github/workflows/ci.yml`):

1. Checkout и установка Python 3.12
2. Установка зависимостей
3. Подъём сервиса PostgreSQL
4. Применение миграций (`--fake-initial`)
5. Запуск flake8 (lint)
6. Проверка схемы OpenAPI
