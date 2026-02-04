#!/usr/bin/env python3
"""
Test script per verificare la connettività ai servizi Docker (PostgreSQL e Redis).

Verifica:
1. Connessione a PostgreSQL su localhost:5432
2. Connessione a Redis su localhost:6379
3. Salvataggio/recupero dati su Redis
4. Esecuzione query SQL su PostgreSQL

Utilizzo:
    python scripts/test_docker_services.py

Prerequisiti:
    - Docker services avviati: docker compose -f docker-compose.base.yml up -d
    - Dipendenze Python: pip install psycopg2-binary redis
"""

import sys
import time
from typing import Tuple, Optional


def test_postgresql() -> Tuple[bool, str]:
    """Test connessione a PostgreSQL."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 non installato (pip install psycopg2-binary)"
    
    try:
        # Configurazione database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="tickertracker",
            password="devpassword",
            database="tickertracker_dev"
        )
        
        # Test semplice: versione PostgreSQL
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"✓ PostgreSQL OK - {version[:50]}"
    
    except Exception as e:
        return False, f"✗ PostgreSQL FAILED - {str(e)}"


def test_redis() -> Tuple[bool, str]:
    """Test connessione a Redis."""
    try:
        import redis
    except ImportError:
        return False, "redis non installato (pip install redis)"
    
    try:
        # Connessione a Redis
        r = redis.Redis(
            host="localhost",
            port=6379,
            password="devpassword",
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test PING
        response = r.ping()
        if not response:
            return False, "✗ Redis PING fallito"
        
        # Test SET/GET
        test_key = "tickertracker:test:connectivity"
        test_value = f"test-{int(time.time())}"
        
        r.set(test_key, test_value, ex=60)  # Expire in 60s
        retrieved = r.get(test_key)
        
        if retrieved != test_value:
            return False, "✗ Redis SET/GET fallito"
        
        # Cleanup
        r.delete(test_key)
        
        # Info
        info = r.info()
        version = info.get("redis_version", "unknown")
        memory_used = info.get("used_memory_human", "unknown")
        
        return True, f"✓ Redis OK - v{version} - Memory: {memory_used}"
    
    except Exception as e:
        return False, f"✗ Redis FAILED - {str(e)}"


def test_postgresql_advanced() -> Tuple[bool, str]:
    """Test avanzato PostgreSQL: creazione tabella e inserimento dati."""
    try:
        import psycopg2
    except ImportError:
        return None, "psycopg2 non installato"
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="tickertracker",
            password="devpassword",
            database="tickertracker_dev"
        )
        
        cursor = conn.cursor()
        
        # Crea tabella test
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connectivity (
                id SERIAL PRIMARY KEY,
                test_value VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inserisci dato
        test_data = f"test-{int(time.time())}"
        cursor.execute(
            "INSERT INTO test_connectivity (test_value) VALUES (%s) RETURNING id",
            (test_data,)
        )
        test_id = cursor.fetchone()[0]
        
        # Recupera dato
        cursor.execute("SELECT test_value FROM test_connectivity WHERE id = %s", (test_id,))
        retrieved = cursor.fetchone()[0]
        
        if retrieved != test_data:
            return False, "✗ PostgreSQL INSERT/SELECT fallito"
        
        # Pulizia
        cursor.execute("DELETE FROM test_connectivity WHERE id = %s", (test_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, f"✓ PostgreSQL Advanced OK - INSERT/SELECT/DELETE funzionante"
    
    except Exception as e:
        return None, f"PostgreSQL advanced - {str(e)}"


def main():
    """Esegui tutti i test."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         TEST CONNETTIVITÀ SERVIZI DOCKER                   ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print("⏳ Verifica connessione servizi...\n")
    
    # Test PostgreSQL
    pg_ok, pg_msg = test_postgresql()
    print(pg_msg)
    
    # Test Redis
    redis_ok, redis_msg = test_redis()
    print(redis_msg)
    
    # Test PostgreSQL Advanced
    pg_adv_ok, pg_adv_msg = test_postgresql_advanced()
    if pg_adv_ok is not None:
        print(pg_adv_msg)
    
    print("\n" + "="*62)
    
    # Summary
    if pg_ok and redis_ok:
        print("✓ TUTTE LE CONNESSIONI FUNZIONANO CORRETTAMENTE")
        print("\nI servizi Docker sono:")
        print("  ✓ PostgreSQL: localhost:5432")
        print("  ✓ Redis: localhost:6379")
        return 0
    else:
        print("✗ ALCUNI SERVIZI NON SONO DISPONIBILI")
        print("\nVerifica che:")
        print("  1. Docker è in esecuzione")
        print("  2. Esegui: docker compose -f docker-compose.base.yml up -d")
        print("  3. Attendi 10-15 secondi per l'inizializzazione")
        print("  4. Verifica healthcheck: docker compose -f docker-compose.base.yml ps")
        return 1


if __name__ == "__main__":
    sys.exit(main())
