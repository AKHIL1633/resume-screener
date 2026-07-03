.PHONY: install migrate run test lint frontend-dev frontend-build docker-up docker-down

install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v --tb=short

lint:
	ruff check .
	ruff format --check .

frontend-dev:
	cd frontend && npm install && npm run dev

frontend-build:
	cd frontend && npm install && npm run build

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v
