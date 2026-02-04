#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Docker Compose management script per TickerTracker services
.DESCRIPTION
    Gestisce lo startup/shutdown/monitoring dei servizi Docker (PostgreSQL, Redis).
    
.EXAMPLE
    .\docker-manage.ps1 up
    .\docker-manage.ps1 down
    .\docker-manage.ps1 status
    .\docker-manage.ps1 logs
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "down", "restart", "status", "ps", "logs", "clean", "health", "help")]
    [string]$Command = "help"
)

$BaseYaml = "docker-compose.base.yml"
$RootDir = Split-Path -Parent $PSScriptRoot

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Text" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Write-Task {
    param([string]$Text)
    Write-Host "→ $Text" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor Cyan
}

# Change to project root
Push-Location $RootDir

switch ($Command.ToLower()) {
    "help" {
        Write-Header "DOCKER COMPOSE - GESTIONE SERVIZI TICKERTRACKER"
        Write-Host "Utilizzo: .\docker-manage.ps1 <comando>`n"
        Write-Host "Comandi:"
        Write-Host "  up        Avvia PostgreSQL e Redis in background"
        Write-Host "  down      Ferma e rimuove i container"
        Write-Host "  restart   Riavvia i container"
        Write-Host "  status    Mostra lo stato dei container"
        Write-Host "  ps        Elenca i container (alias di status)"
        Write-Host "  logs      Mostra i log dei servizi (follow mode)"
        Write-Host "  health    Verifica lo stato healthcheck"
        Write-Host "  clean     Rimuove volumi e dati (ATTENZIONE!)"
        Write-Host "  help      Mostra questo messaggio`n"
        Write-Host "Esempi:"
        Write-Host "  .\docker-manage.ps1 up         # Avvia servizi"
        Write-Host "  .\docker-manage.ps1 logs       # Mostra log in real-time"
        Write-Host "  .\docker-manage.ps1 down       # Ferma servizi"
    }
    
    "up" {
        Write-Header "AVVIO SERVIZI DOCKER"
        Write-Task "Avvio PostgreSQL 16 e Redis 7..."
        docker-compose -f $BaseYaml up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Servizi avviati"
            Write-Host ""
            Write-Info "Servizi disponibili:"
            Write-Host "  PostgreSQL: localhost:5432 (user: tickertracker, password: devpassword)"
            Write-Host "  Redis: localhost:6379 (password: devpassword)"
            Write-Host ""
            Write-Task "Attesa inizializzazione servizi (10-15 secondi)..."
            Start-Sleep -Seconds 5
            
            Write-Task "Verifica stato healthcheck..."
            docker-compose -f $BaseYaml ps
        } else {
            Write-Error "Errore nell'avvio dei servizi"
            Pop-Location
            exit 1
        }
    }
    
    "down" {
        Write-Header "ARRESTO SERVIZI DOCKER"
        Write-Task "Arresto container..."
        docker-compose -f $BaseYaml down
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Servizi arrestati"
        } else {
            Write-Error "Errore nell'arresto dei servizi"
        }
    }
    
    "restart" {
        Write-Header "RIAVVIO SERVIZI DOCKER"
        Write-Task "Riavvio container..."
        docker-compose -f $BaseYaml restart
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Servizi riavviati"
            Write-Task "Attesa stabilizzazione (5 secondi)..."
            Start-Sleep -Seconds 5
            
            docker-compose -f $BaseYaml ps
        }
    }
    
    {$_ -in "status", "ps"} {
        Write-Header "STATO SERVIZI DOCKER"
        docker-compose -f $BaseYaml ps
    }
    
    "health" {
        Write-Header "VERIFICA HEALTHCHECK"
        Write-Task "Esecuzione diagnostica..."
        
        # Check PostgreSQL
        Write-Host ""
        Write-Info "PostgreSQL:"
        docker exec tickertracker-postgres pg_isready -U tickertracker
        if ($LASTEXITCODE -eq 0) {
            Write-Success "PostgreSQL is ready"
        } else {
            Write-Error "PostgreSQL NOT ready"
        }
        
        # Check Redis
        Write-Host ""
        Write-Info "Redis:"
        docker exec tickertracker-redis redis-cli --raw incr ping
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Redis is ready"
        } else {
            Write-Error "Redis NOT ready"
        }
        
        Write-Host ""
        Write-Task "Verifica complete view..."
        docker-compose -f $BaseYaml ps
    }
    
    "logs" {
        Write-Header "LOG SERVIZI DOCKER"
        Write-Info "Seguendo log in real-time (Ctrl+C per uscire)..."
        Write-Host ""
        docker-compose -f $BaseYaml logs -f
    }
    
    "clean" {
        Write-Header "PULIZIA SERVIZI DOCKER"
        Write-Error "⚠️  ATTENZIONE: Questo comando rimuoverà TUTTI i dati persistenti!"
        
        $response = Read-Host "Continua? (s/n)"
        if ($response -ne "s") {
            Write-Info "Pulizia annullata"
            Pop-Location
            exit 0
        }
        
        Write-Task "Arresto servizi..."
        docker-compose -f $BaseYaml down -v
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Servizi, container e volumi rimossi"
        }
    }
    
    default {
        Write-Error "Comando sconosciuto: $Command"
        Write-Host "Esegui '.\docker-manage.ps1 help' per vedere i comandi disponibili"
        Pop-Location
        exit 1
    }
}

Pop-Location
