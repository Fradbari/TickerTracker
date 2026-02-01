#!/bin/bash
# Script per il controllo centralizzato della qualità del codice (Linting & Type Checking)

set -e

# Colori per l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"

echo -e "${BLUE}=== Avvio Controlli Qualità TickerTracker v3.0 ===${NC}"

# 1. Backend Linting (Ruff)
echo -e "\n${BLUE}--- Backend: Ruff (Linting & Formatting) ---${NC}"
cd "$ROOT_DIR/backend"
python3 -m ruff check src tests
python3 -m ruff format --check src tests

# 2. Backend Type Checking (MyPy)
echo -e "\n${BLUE}--- Backend: MyPy (Type Checking) ---${NC}"
python3 -m mypy src

# 3. Frontend Linting (ESLint)
echo -e "\n${BLUE}--- Frontend: ESLint ---${NC}"
cd "$ROOT_DIR/frontend"
# Assicuriamoci che eslint sia eseguibile e usiamo la versione locale
chmod +x node_modules/.bin/eslint 2>/dev/null || true
npm run lint

# 4. Frontend Type Checking (TSC)
echo -e "\n${BLUE}--- Frontend: Type Checking (tsc) ---${NC}"
npm run type-check

echo -e "\n${GREEN}=== Tutti i controlli qualità superati! ===${NC}"
