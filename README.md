Donut Tracker API
CRUD REST API для управления групповыми денежными сборами.
Проект разработан с использованием Django REST Framework, PostgreSQL и Redis.

Функционал
Кастомная модель пользователя
Управление сборами и платежами (CRUD операции)
Автоматическое обновление сумм сборов через сигналы
Уведомления о завершении сборов
Логирование email-уведомлений
Кэширование данных с использованием django-redis
Генерация тестовых данных с помощью Faker
Автогенерация OpenAPI документации через drf-spectacular
Технологический стек
Python 3.11
Django 5
Django REST Framework
PostgreSQL
Redis
Docker + Docker Compose

# Установка и запуск
# Предварительные требования
Docker
Docker Compose

# Настройка окружения
Создайте файл .env в корне проекта:

SECRET_KEY=your-secret-key-here
DEBUG=True
POSTGRES_DB=donut_tracker
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/1

# Запуск приложения

# Клонирование репозитория
git clone git@github.com:Dmitriy1689/donut_tracker.git
cd donut_tracker

# Запуск контейнеров
docker-compose up -d --build

# Выполнение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Заполнение тестовыми данными (опционально)
docker-compose exec web python manage.py fill_db --users 5 --collects 3 --payments 10

# Доступные эндпоинты
API документация: http://127.0.0.1:8000/api/v1/docs/
Административная панель: http://127.0.0.1:8000/admin/
Сборы: http://127.0.0.1:8000/api/v1/collects/
Платежи: http://127.0.0.1:8000/api/v1/payments/
Аутентификация: http://127.0.0.1:8000/api/v1/api-token-auth/

# Структура проекта
donut_tracker/
├── config/           # Настройки Django
├── collects/         # Приложение для денежных сборов
├── payments/         # Приложение для платежей
├── users/            # Приложение пользователей
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example

# Использование API
Аутентификация
# Получение токена
curl -X POST http://127.0.0.1:8000/api/v1/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Использование токена
curl -H "Authorization: Token your_token_here" http://127.0.0.1:8000/api/v1/collects/

# Примеры запросов
Создание сбора:

curl -X POST http://127.0.0.1:8000/api/v1/collects/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Сбор на лечение",
    "description": "Сбор средств на медицинские расходы",
    "occasion": "medicine",
    "target_amount": 50000,
    "end_datetime": "2024-12-31T23:59:59Z"
  }'

# Создание платежа:

curl -X POST http://127.0.0.1:8000/api/v1/payments/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "collect": 1,
    "amount": 1000,
    "hide_amount": false
  }'
# Команды управления
# Заполнение тестовыми данными
python manage.py fill_db --users 10 --collects 5 --payments 20

Особенности реализации
Автоматическое обновление текущей суммы и количества донатеров при создании/удалении платежей
Валидация суммы платежей относительно целевой суммы сбора
Кэширование GET-запросов для повышения производительности
JWT-аутентификация для защиты API endpoints
Фильтрация платежей по идентификатору сбора
Автоматическое закрытие сбора при достижении целевой суммы