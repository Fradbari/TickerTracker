.PHONY: help install install-pip lint format typecheck test test-cov test-unit test-integration test-e2e run check-deps export-requirements clean

.DEFAULT_GOAL := help

help: ## Mostra questo messaggio di aiuto
	@echo "Comandi disponibili:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installa dipendenze con Poetry
	poetry install

install-pip: ## Installa dipendenze con pip (fallback)
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint: ## Esegui linting con ruff
	ruff check src/

format: ## Formatta codice con black e ruff
	black src/ tests/
	ruff check src/ --fix

typecheck: ## Esegui type checking con mypy
	mypy src/

test: ## Esegui tutti i test
	pytest tests/

test-cov: ## Esegui test con coverage report
	pytest --cov=src --cov-report=html --cov-report=term tests/

test-unit: ## Esegui solo unit tests
	pytest -m unit tests/

test-integration: ## Esegui solo integration tests
	pytest -m integration tests/

test-e2e: ## Esegui solo E2E tests
	pytest -m e2e tests/

run: ## Avvia server uvicorn in modalità dev
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

check-deps: ## Verifica installazione dipendenze
	python scripts/check_deps.py

export-requirements: ## Rigenera requirements.txt da pyproject.toml
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

clean: ## Rimuovi file temporanei e cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

# Database migrations
migrate: ## Applica migrazioni database
	alembic upgrade head

migrate-down: ## Rollback ultima migrazione
	alembic downgrade -1

migrate-new: ## Crea nuova migrazione auto-generata
	@read -p "Inserisci messaggio migrazione: " msg; \
	alembic revision --autogenerate -m "$$msg"
