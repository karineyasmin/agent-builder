.PHONY: help install lock lint type-check test test-cov run docker-up docker-down docker-logs logs clean

UV := uv

help:
	@echo "Comandos disponíveis (uv workflow):"
	@echo "  make install      Instala dependências com sync exato do lockfile"
	@echo "  make lock         Gera ou atualiza uv.lock"
	@echo "  make lint         Executa ruff (linter e formatação)"
	@echo "  make type-check   Executa checagem de tipos estrita com mypy"
	@echo "  make test         Executa suite de testes unitários"
	@echo "  make test-cov     Executa testes com relatório de cobertura"
	@echo "  make run          Inicia o FastAPI com hot-reload"
	@echo "  make docker-up    Sobe o ambiente via docker compose em background"
	@echo "  make docker-down  Derruba os containers"
	@echo "  make logs         Acompanha os logs dos containers em tempo real"

install:
	$(UV) sync --all-groups

lock:
	$(UV) lock

lint:
	$(UV) run ruff check app tests
	$(UV) run ruff format --check app tests

type-check:
	$(UV) run mypy app

test:
	$(UV) run pytest -v tests/

test-cov:
	$(UV) run pytest -v --cov=app --cov-report=term-missing tests/

run:
	$(UV) run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

docker-logs:
	docker compose logs -f --tail=100 -t

logs: docker-logs

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage