#!/usr/bin/env bash
#
# Docker Compose management script per TickerTracker services
# Gestisce lo startup/shutdown/monitoring dei servizi Docker (PostgreSQL, Redis)
#
# Utilizzo:
#   ./docker-manage.sh up
#   ./docker-manage.sh down
#   ./docker-manage.sh status
#   ./docker-manage.sh logs
#

set -e

BASE_YAML="docker-compose.base.yml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_task() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Main command handler
case "${1:-help}" in
    up)
        print_header "AVVIO SERVIZI DOCKER"
        print_task "Avvio PostgreSQL 16 e Redis 7..."
        docker compose -f "$BASE_YAML" up -d
        
        if [ $? -eq 0 ]; then
            print_success "Servizi avviati"
            echo ""
            print_info "Servizi disponibili:"
            echo "  PostgreSQL: localhost:5432 (user: tickertracker, password: devpassword)"
            echo "  Redis: localhost:6379 (password: devpassword)"
            echo ""
            print_task "Attesa inizializzazione servizi (10-15 secondi)..."
            sleep 5
            
            print_task "Verifica stato healthcheck..."
            docker compose -f "$BASE_YAML" ps
        else
            print_error "Errore nell'avvio dei servizi"
            exit 1
        fi
        ;;
    
    down)
        print_header "ARRESTO SERVIZI DOCKER"
        print_task "Arresto container..."
        docker compose -f "$BASE_YAML" down
        
        if [ $? -eq 0 ]; then
            print_success "Servizi arrestati"
        else
            print_error "Errore nell'arresto dei servizi"
            exit 1
        fi
        ;;
    
    restart)
        print_header "RIAVVIO SERVIZI DOCKER"
        print_task "Riavvio container..."
        docker compose -f "$BASE_YAML" restart
        
        if [ $? -eq 0 ]; then
            print_success "Servizi riavviati"
            print_task "Attesa stabilizzazione (5 secondi)..."
            sleep 5
            
            docker compose -f "$BASE_YAML" ps
        fi
        ;;
    
    status|ps)
        print_header "STATO SERVIZI DOCKER"
        docker compose -f "$BASE_YAML" ps
        ;;
    
    health)
        print_header "VERIFICA HEALTHCHECK"
        print_task "Esecuzione diagnostica..."
        
        # Check PostgreSQL
        echo ""
        print_info "PostgreSQL:"
        docker exec tickertracker-postgres pg_isready -U tickertracker
        if [ $? -eq 0 ]; then
            print_success "PostgreSQL is ready"
        else
            print_error "PostgreSQL NOT ready"
        fi
        
        # Check Redis
        echo ""
        print_info "Redis:"
        docker exec tickertracker-redis redis-cli --raw incr ping
        if [ $? -eq 0 ]; then
            print_success "Redis is ready"
        else
            print_error "Redis NOT ready"
        fi
        
        echo ""
        print_task "Verifica complete view..."
        docker compose -f "$BASE_YAML" ps
        ;;
    
    logs)
        print_header "LOG SERVIZI DOCKER"
        print_info "Seguendo log in real-time (Ctrl+C per uscire)..."
        echo ""
        docker compose -f "$BASE_YAML" logs -f
        ;;
    
    clean)
        print_header "PULIZIA SERVIZI DOCKER"
        print_error "⚠️  ATTENZIONE: Questo comando rimuoverà TUTTI i dati persistenti!"
        echo ""
        
        read -p "Continua? (s/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Pulizia annullata"
            exit 0
        fi
        
        print_task "Arresto servizi..."
        docker compose -f "$BASE_YAML" down -v
        
        if [ $? -eq 0 ]; then
            print_success "Servizi, container e volumi rimossi"
        fi
        ;;
    
    help)
        print_header "DOCKER COMPOSE - GESTIONE SERVIZI TICKERTRACKER"
        echo "Utilizzo: ./docker-manage.sh <comando>"
        echo ""
        echo "Comandi:"
        echo "  up        Avvia PostgreSQL e Redis in background"
        echo "  down      Ferma e rimuove i container"
        echo "  restart   Riavvia i container"
        echo "  status    Mostra lo stato dei container"
        echo "  ps        Elenca i container (alias di status)"
        echo "  logs      Mostra i log dei servizi (follow mode)"
        echo "  health    Verifica lo stato healthcheck"
        echo "  clean     Rimuove volumi e dati (ATTENZIONE!)"
        echo "  help      Mostra questo messaggio"
        echo ""
        echo "Esempi:"
        echo "  ./docker-manage.sh up         # Avvia servizi"
        echo "  ./docker-manage.sh logs       # Mostra log in real-time"
        echo "  ./docker-manage.sh down       # Ferma servizi"
        ;;
    
    *)
        print_error "Comando sconosciuto: $1"
        echo "Esegui './docker-manage.sh help' per vedere i comandi disponibili"
        exit 1
        ;;
esac
