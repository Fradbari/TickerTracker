#!/bin/bash
# Script per l'esecuzione unificata di tutti i test (Backend e Frontend)

set -e

# Colori per l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"

echo -e "${BLUE}=== Avvio Test Suite TickerTracker v3.0 ===${NC}"

# 1. Test Backend
echo -e "\n${BLUE}--- Esecuzione Test Backend (Python/pytest) ---${NC}"
cd "$ROOT_DIR/backend"
PYTHONPATH=. python3 -m pytest tests/unit/ --cov=src --cov-report=term-missing -n auto

# 2. Test Frontend
echo -e "\n${BLUE}--- Esecuzione Test Frontend (React/vitest) ---${NC}"
cd "$ROOT_DIR/frontend"
# Assicuriamoci che vitest sia eseguibile (fix per problemi di permessi in alcuni ambienti)
chmod +x node_modules/.bin/vitest 2>/dev/null || true
npm test -- --run --coverage

echo -e "\n${GREEN}=== Tutti i test completati con successo! ===${NC}"
