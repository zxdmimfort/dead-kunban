.PHONY: dev

dev:
	@echo "Starting backend and frontend..."
	# Запускаем бекенд в фоне
	(cd backend && fastapi dev src) &
	# Запускаем фронтенд в фоне
	(cd frontend && npm run dev) &
	wait

