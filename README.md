## Startup dev server
```sh
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install dependencies
uv sync
# Start dev server
fastapi dev src
# or
uvicorn src.main:app --reload
```

## Install pre-commit hooks
```sh
pre-commit install
```

## Запуск линтера/форматера
```sh
ruff check --fix . && ruff format .
```

## Добавление/изменение моделей бд
```sh
# Создаем файл миграции
alembic revision --autogenerate
# Проводим миграцию
alembic upgrade head
```

## Node.js
```sh
# скачивание модулей nodejs
npm install
# запуск дев сервера
npm run dev
```
