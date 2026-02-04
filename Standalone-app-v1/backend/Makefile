.PHONY: help install install-pip lint format typecheck test test-cov test-unit test-integration test-e2e run check-deps export-requirements clean venv

.DEFAULT_GOAL := help

help: ## Mostra questo messaggio di aiuto
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║        TICKERTRACKER BACKEND - COMANDI DISPONIBILI        ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Crea virtual environment Python
	python -m venv venv

install: check-deps ## Installa dipendenze con Poetry
	@echo "🔧 Installazione dipendenze con Poetry..."
	poetry install
	@echo "✓ Installazione completata"
	@echo "Esegui: poetry shell oppure source venv/bin/activate"

install-pip: ## Installa dipendenze con pip (fallback)
	@echo "🔧 Installazione dipendenze con pip..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "✓ Installazione completata"

lint: ## Esegui linting con ruff
	@echo "🔍 Linting con Ruff..."
	ruff check src/ tests/
	@echo "✓ Linting completato"

format: ## Formatta codice con ruff
	@echo "✨ Formattazione codice..."
	ruff format src/ tests/
	ruff check src/ tests/ --fix
	@echo "✓ Formattazione completata"

typecheck: ## Esegui type checking con mypy
	@echo "🔍 Type checking con Mypy..."
	mypy src/
	@echo "✓ Type checking completato"

test: ## Esegui tutti i test
	@echo "🧪 Esecuzione test..."
	pytest tests/ -v

test-cov: ## Esegui test con coverage report
	@echo "🧪 Esecuzione test con coverage..."
	pytest --cov=src --cov-report=html --cov-report=term tests/
	@echo "✓ Report HTML disponibile in htmlcov/index.html"

test-unit: ## Esegui solo unit tests
	@echo "🧪 Esecuzione unit tests..."
	pytest -m unit tests/ -v

test-integration: ## Esegui solo integration tests
	@echo "🧪 Esecuzione integration tests..."
	pytest -m integration tests/ -v

test-e2e: ## Esegui solo E2E tests
	@echo "🧪 Esecuzione E2E tests..."
	pytest -m e2e tests/ -v

run: ## Avvia server uvicorn in modalità dev
	@echo "🚀 Avvio server FastAPI (dev mode)..."
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

check-deps: ## Verifica installazione dipendenze critiche
	@python scripts/check_deps.py

export-requirements: ## Rigenera requirements.txt da pyproject.toml
	@echo "📝 Generazione requirements.txt..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	@echo "📝 Generazione requirements-dev.txt..."
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
	@echo "✓ File requirements.txt e requirements-dev.txt aggiornati"

clean: ## Rimuove cache e file temporanei
	@echo "🧹 Pulizia cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "✓ Pulizia completata"

all: clean check-deps lint typecheck test ## Esegui tutti i controlli (lint, type, test)clean: ## Rimuovi file temporanei e cache
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
