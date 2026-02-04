#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script per TickerTracker Backend (alternativa a Make su Windows)
.DESCRIPTION
    Esegue comandi comuni per lo sviluppo del backend.
.EXAMPLE
    .\build.ps1 help
    .\build.ps1 check-deps
    .\build.ps1 lint
#>

param(
    [Parameter(Position = 0)]
    [string]$Task = "help",
    
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Text" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Task {
    param([string]$Text)
    Write-Host "→ $Text" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

switch ($Task.ToLower()) {
    "help" {
        Write-Header "TICKERTRACKER BACKEND - COMANDI DISPONIBILI"
        Write-Host "Utilizzo: .\build.ps1 <comando>`n"
        Write-Host "Comandi:"
        Write-Host "  venv              Crea virtual environment Python"
        Write-Host "  install           Installa dipendenze con Poetry"
        Write-Host "  install-pip       Installa dipendenze con pip (fallback)"
        Write-Host "  check-deps        Verifica dipendenze critiche"
        Write-Host "  lint              Esegui linting con ruff"
        Write-Host "  format            Formatta codice con ruff"
        Write-Host "  typecheck         Esegui type checking con mypy"
        Write-Host "  test              Esegui tutti i test"
        Write-Host "  test-cov          Esegui test con coverage report"
        Write-Host "  test-unit         Esegui solo unit tests"
        Write-Host "  test-integration  Esegui solo integration tests"
        Write-Host "  test-e2e          Esegui solo E2E tests"
        Write-Host "  run               Avvia server FastAPI (dev mode)"
        Write-Host "  export-requirements  Rigenera requirements.txt"
        Write-Host "  clean             Rimuove cache e file temporanei"
        Write-Host "  all               Esegui tutti i controlli (lint, type, test)"
        Write-Host ""
    }
    
    "venv" {
        Write-Task "Creazione virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment creato"
        Write-Host "Attiva con: .\venv\Scripts\Activate.ps1"
    }
    
    "install" {
        Write-Task "Verifica dipendenze..."
        python scripts/check_deps.py
        Write-Task "Installazione dipendenze con Poetry..."
        poetry install
        Write-Success "Installazione completata"
    }
    
    "install-pip" {
        Write-Task "Installazione dipendenze con pip..."
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        Write-Success "Installazione completata"
    }
    
    "check-deps" {
        python scripts/check_deps.py
    }
    
    "lint" {
        Write-Task "Linting con Ruff..."
        ruff check src/ tests/ 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Linting completato"
        }
    }
    
    "format" {
        Write-Task "Formattazione codice..."
        ruff format src/ tests/
        ruff check src/ tests/ --fix 2>$null
        Write-Success "Formattazione completata"
    }
    
    "typecheck" {
        Write-Task "Type checking con Mypy..."
        mypy src/
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Type checking completato"
        }
    }
    
    "test" {
        Write-Task "Esecuzione test..."
        pytest tests/ -v
    }
    
    "test-cov" {
        Write-Task "Esecuzione test con coverage..."
        pytest --cov=src --cov-report=html --cov-report=term tests/
        Write-Success "Report HTML disponibile in htmlcov/index.html"
    }
    
    "test-unit" {
        Write-Task "Esecuzione unit tests..."
        pytest -m unit tests/ -v
    }
    
    "test-integration" {
        Write-Task "Esecuzione integration tests..."
        pytest -m integration tests/ -v
    }
    
    "test-e2e" {
        Write-Task "Esecuzione E2E tests..."
        pytest -m e2e tests/ -v
    }
    
    "run" {
        Write-Task "Avvio server FastAPI (dev mode)..."
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    }
    
    "export-requirements" {
        Write-Task "Generazione requirements.txt..."
        poetry export -f requirements.txt --output requirements.txt --without-hashes
        Write-Task "Generazione requirements-dev.txt..."
        poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
        Write-Success "File requirements.txt e requirements-dev.txt aggiornati"
    }
    
    "clean" {
        Write-Task "Pulizia cache..."
        
        Get-ChildItem -Path . -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -File -Filter *.pyc -Recurse | Remove-Item -Force
        Get-ChildItem -Path . -Directory -Filter .pytest_cache -Recurse | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Directory -Filter .mypy_cache -Recurse | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Directory -Filter htmlcov -Recurse | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -File -Filter .coverage -Recurse | Remove-Item -Force
        
        Write-Success "Pulizia completata"
    }
    
    "all" {
        Write-Header "ESECUZIONE TUTTI I CONTROLLI"
        Write-Host ""
        
        Write-Task "Pulizia cache..."
        & $PSScriptRoot\build.ps1 clean
        
        Write-Host ""
        Write-Task "Verifica dipendenze..."
        python scripts/check_deps.py
        
        Write-Host ""
        Write-Task "Linting..."
        & $PSScriptRoot\build.ps1 lint
        
        Write-Host ""
        Write-Task "Type checking..."
        & $PSScriptRoot\build.ps1 typecheck
        
        Write-Host ""
        Write-Task "Test con coverage..."
        & $PSScriptRoot\build.ps1 test-cov
        
        Write-Success "Tutti i controlli completati!"
    }
    
    default {
        Write-Error "Comando sconosciuto: $Task"
        Write-Host "Esegui '.\build.ps1 help' per vedere i comandi disponibili"
        exit 1
    }
}
