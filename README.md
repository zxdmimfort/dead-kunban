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

## Запуск линтера/форматера
```sh
ruff check --fix . && ruff format .
```
