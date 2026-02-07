# Alembic Setup and Migration Guide

## ✅ Correzioni Completate

### Task 2.7 Fixes:
1. ✅ **shared/domain/__init__.py** - Aggiunto export di User, Role, RoleType, user_roles
2. ✅ **User.is_active index** - Aggiunto indice su User.is_active
3. ✅ **verify_task_2_7.py** - Creato script di verifica con 8 test suite (TUTTI PASSATI)

### Task 2.10 Fixes:
4. ✅ **env.py target_metadata** - Importati tutti i modelli (Ticker, MarketData, Estimate, EstimateEvent, User, Role, AiModelRun, SyncJob)
5. ✅ **alembic.ini script_location** - Corretto path da "backend/alembic" a "alembic"
6. ✅ **alembic/versions directory** - Verificata esistenza della directory

## ⚠️ Database Setup Richiesto

Per completare la generazione delle migrations, è necessario avere un database PostgreSQL in esecuzione.

### Opzione 1: Avviare PostgreSQL con Docker

```bash
# Nel terminale, dalla directory backend/
docker-compose up -d postgres
```

### Opzione 2: Configurare DATABASE_URL

Creare un file `.env` nella directory `backend/`:

```bash
# Copia .env.example
cp .env.example .env
```

Modifica il file `.env` con le credenziali corrette:

```env
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/tickertracker
```

## 📋 Comandi Alembic

Una volta configurato il database:

```bash
# 1. Genera migration iniziale
alembic revision --autogenerate -m "Initial models: Ticker, Estimate, EstimateEvent, MarketData, User, Role"

# 2. Verifica migration generata
ls alembic/versions/

# 3. Applica migration al database
alembic upgrade head

# 4. Verifica stato migrations
alembic current

# 5. Downgrade (se necessario)
alembic downgrade -1
```

## 📁 Struttura File Corretti

```
backend/
├── alembic/
│   ├── versions/          ✅ Directory esistente
│   ├── env.py             ✅ Configurato con tutti i modelli
│   ├── script.py.mako     ✅ Template migration
│   └── README             ✅ Documentazione Alembic
├── alembic.ini            ✅ Configurato con script_location = alembic
├── src/
│   ├── shared/
│   │   └── domain/
│   │       ├── __init__.py       ✅ Export User, Role, RoleType, user_roles
│   │       └── user.py           ✅ User con index su is_active
│   ├── market_data/domain/
│   ├── estimates/domain/
│   ├── analytics/domain/
│   └── sync/domain/
└── verify_task_2_7.py     ✅ Test script (8/8 test passati)
```

## ✅ Modelli Registrati in Alembic

I seguenti modelli sono ora correttamente importati in `alembic/env.py`:

1. **market_data.domain.entities.Ticker**
2. **market_data.domain.market_data.MarketData**
3. **estimates.domain.entities.Estimate**
4. **estimates.domain.events.EstimateEvent**
5. **analytics.domain.entities.AiModelRun**
6. **sync.domain.entities.SyncJob**
7. **shared.domain.user.User**
8. **shared.domain.user.Role**

## 🔧 Prossimi Passi

1. Avviare il database PostgreSQL
2. Configurare DATABASE_URL (se non già fatto)
3. Eseguire `alembic revision --autogenerate`
4. Verificare la migration generata
5. Applicare con `alembic upgrade head`
