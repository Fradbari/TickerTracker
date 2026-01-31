#!/usr/bin/env python3
"""
Script per verificare che tutte le dipendenze critiche siano installate correttamente.
"""
import sys
from typing import List, Tuple

def check_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Prova ad importare un modulo e restituisce (success, message)"""
    pkg = package_name or module_name
    try:
        __import__(module_name)
        return True, f"✓ {pkg}"
    except ImportError as e:
        return False, f"✗ {pkg}: {str(e)}"

def main():
    checks = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("sqlalchemy", "sqlalchemy"),
        ("alembic", "alembic"),
        ("redis", "redis"),
        ("yfinance", "yfinance"),
        ("googleapiclient", "google-api-python-client"),
        ("google.auth", "google-auth"),
        ("cryptography", "cryptography"),
        ("apscheduler", "apscheduler"),
        ("pytest", "pytest"),
    ]
    
    results: List[Tuple[bool, str]] = []
    for module, package in checks:
        results.append(check_import(module, package))
    
    print("\n=== Verifica Dipendenze ===")
    print()
    for success, message in results:
        print(message)
    
    failed = [msg for success, msg in results if not success]
    
    if failed:
        print(f"\n✗ {len(failed)} dipendenze mancanti")
        print("\nEsegui: make install oppure make install-pip")
        return 1
    else:
        print(f"\n✓ Tutte le {len(results)} dipendenze sono installate correttamente!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
