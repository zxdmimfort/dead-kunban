.PHONY: dev setup

dev:
	@echo "Starting backend and frontend..."
	# Запускаем бекенд в фоне
	(cd backend && fastapi dev src) &
	# Запускаем фронтенд в фоне
	(cd frontend && npm run dev) &
	wait


setup:
	@echo "Installing and configuring dependencies..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh && \
	uv sync && \
	uv run pre-commit install && \
	cd frontend && npm install