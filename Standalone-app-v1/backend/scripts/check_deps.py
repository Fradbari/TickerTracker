#!/usr/bin/env python3
"""
Script per verificare che tutte le dipendenze critiche siano installate correttamente.
Verifica le dipendenze del file pyproject.toml e segnala eventuali problemi.
"""
import sys

# CRITICAL DEPENDENCIES - Devono essere presenti sempre
CRITICAL_DEPS = [
    ("fastapi", "FastAPI - Web Framework"),
    ("uvicorn", "Uvicorn - ASGI Server"),
    ("pydantic", "Pydantic - Data Validation"),
    ("sqlalchemy", "SQLAlchemy - ORM/Database"),
    ("asyncpg", "AsyncPG - PostgreSQL Driver"),
    ("redis", "Redis - Cache Client"),
    ("yfinance", "YFinance - Market Data"),
    ("googleapiclient", "Google API Client"),
    ("apscheduler", "APScheduler - Job Scheduling"),
]

# OPTIONAL DEPENDENCIES - Per funzionalità specifiche
OPTIONAL_DEPS = [
    ("cryptography", "Cryptography - Security"),
    ("google.auth", "Google Auth - Authentication"),
    ("prometheus_client", "Prometheus - Metrics"),
    ("structlog", "Structlog - Structured Logging"),
    ("slowapi", "SlowAPI - Rate Limiting"),
]

# DEV DEPENDENCIES - Solo per sviluppo
DEV_DEPS = [
    ("pytest", "Pytest - Testing Framework"),
    ("pytest_asyncio", "Pytest AsyncIO - Async Testing"),
    ("pytest_cov", "Pytest Coverage - Coverage Reports"),
    ("mypy", "Mypy - Type Checker"),
    ("ruff", "Ruff - Code Linter/Formatter"),
    ("httpx", "HTTPX - HTTP Client"),
]

def check_import(module_name: str, display_name: str) -> tuple[bool, str]:
    """
    Prova ad importare un modulo e restituisce (success, message).
    Supporta nomi con punto per sottommoduli (es: google.auth).
    """
    try:
        if "." in module_name:
            # Importa il primo livello
            base = module_name.split(".")[0]
            __import__(base)
        else:
            __import__(module_name)
        return True, f"  ✓ {display_name}"
    except ImportError as e:
        return False, f"  ✗ {display_name}: {str(e)}"

def check_python_version() -> tuple[bool, str]:
    """Verifica che la versione Python sia >= 3.11"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"✗ Python {version.major}.{version.minor}.{version.micro} (richiesto: >=3.11)"

def main():
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║           VERIFICA DIPENDENZE TICKERTRACKER BACKEND         ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")

    # Verifica versione Python
    py_ok, py_msg = check_python_version()
    print(f"[Python] {py_msg}")

    # Verifica dipendenze critiche
    print("\n[DIPENDENZE CRITICHE] (Obbligatorie)")
    critical_results = []
    for module, display_name in CRITICAL_DEPS:
        ok, msg = check_import(module, display_name)
        critical_results.append((ok, msg))
        print(msg)

    # Verifica dipendenze opzionali
    print("\n[DIPENDENZE OPZIONALI] (Fase 2)")
    optional_results = []
    for module, display_name in OPTIONAL_DEPS:
        ok, msg = check_import(module, display_name)
        optional_results.append((ok, msg))
        print(msg)

    # Verifica dipendenze di sviluppo
    print("\n[DIPENDENZE SVILUPPO] (Dev/Testing)")
    dev_results = []
    for module, display_name in DEV_DEPS:
        ok, msg = check_import(module, display_name)
        dev_results.append((ok, msg))
        print(msg)

    # Riepilogo
    print("\n" + "="*65)
    critical_failed = [msg for ok, msg in critical_results if not ok]
    optional_failed = [msg for ok, msg in optional_results if not ok]
    dev_failed = [msg for ok, msg in dev_results if not ok]

    if critical_failed:
        print(f"✗ {len(critical_failed)} DIPENDENZA/E CRITICA/E MANCANTE/I:")
        for msg in critical_failed:
            print(msg)
        print("\nEsegui uno di questi comandi:")
        print("  • poetry install")
        print("  • make install")
        print("  • pip install -r requirements.txt")
        return 1
    else:
        total = len(critical_results) + len(optional_results) + len(dev_results)
        missing = len(optional_failed) + len(dev_failed)
        if missing > 0:
            print(f"✓ Tutte le dipendenze CRITICHE ({len(critical_results)}) sono installate")
            print(f"⚠ {missing} dipendenze OPZIONALI o DEV mancanti (non critico)")
            return 0
        else:
            print(f"✓ Tutte le {total} dipendenze sono installate correttamente!")
            print("✓ Sistema pronto per lo sviluppo")
            return 0

if __name__ == "__main__":
    sys.exit(main())

if __name__ == "__main__":
    sys.exit(main())
