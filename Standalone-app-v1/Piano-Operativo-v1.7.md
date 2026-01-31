# Piano Operativo TickerTracker v3.0
**Versione:** 1.7  
**Data:** 31 Gennaio 2026  
**Stato:** Pianificazione Completa

---

## 🎯 Executive Summary

**TickerTracker v3.0** è una riscrittura completa della piattaforma di tracking stime trading, con focus su:

- ✅ **Architettura moderna**: DDD + CQRS + Event Sourcing
- ✅ **Precisione finanziaria**: Decimal-based calculations
- ✅ **Scalabilità**: Da single-user locale a multi-tenant cloud
- ✅ **Affidabilità**: Testing completo e CI/CD automatizzato
- ✅ **Retrocompatibilità**: Migrazione dati da v2.4 preservata

---

## 🏗️ Architettura

### Principi Architetturali

#### 1. Domain-Driven Design (DDD)

**Bounded Context Identificati:**

- **Estimates**: Gestione stime Long/Short, lifecycle, eventi
- **Market Data**: Prezzi real-time, cache, provider esterni
- **Sync**: Sincronizzazione bidirezionale con Google Drive
- **Analytics**: Calcolo P&L, metriche performance, report
- **Auth** (Fase 2): User management, RBAC, JWT

**Value Objects:**
- `Money`: Gestione importi con currency e precisione Decimal
- `Percentage`: Gestione percentuali con basis points
- `PriceTarget`: Validazione target/stop per direzione (LONG/SHORT)

#### 2. CQRS (Command Query Responsibility Segregation)

**Command Side:**
- Write operations tramite `EstimateService`
- Validazione business rules
- Generazione eventi dominio

**Query Side:**
- Read operations tramite Materialized Views
- `EstimateSummaryView` per dashboard performance
- Cache Redis per query frequenti

#### 3. Event Sourcing

**Event Store:**
- Tabella `estimate_events` per audit trail completo
- Eventi: `EstimateCreated`, `EstimateUpdated`, `TargetHit`, `StopHit`, `EstimateClosed`
- Ricostruzione stato da eventi per analisi storiche

**Outbox Pattern** (Fase 2):
- Garantisce eventual consistency
- Pubblicazione eventi su message broker

---

## 💻 Tech Stack

### Backend

| Componente | Tecnologia | Versione | Motivazione |
|-----------|-----------|---------|-------------|
| **Runtime** | Python | 3.11+ | Type hints, performance, ecosystem |
| **Framework** | FastAPI | Latest | Async, OpenAPI auto-gen, performance |
| **Database** | PostgreSQL | 16 | Materialized views, JSON, performance |
| **ORM** | SQLAlchemy | 2.0+ | Async support, type safety |
| **Migrations** | Alembic | Latest | SQLAlchemy integration |
| **Cache** | Redis | 7 | Rate limiting, session, cache |
| **Validation** | Pydantic | 2.0+ | Data validation, settings management |
| **Task Queue** | APScheduler | Latest | Background jobs, scheduling |
| **Market Data** | yfinance | Latest | Yahoo Finance integration |
| **Cloud Sync** | Google Drive API | v3 | Backup e sync dati |

### Frontend

| Componente | Tecnologia | Versione | Motivazione |
|-----------|-----------|---------|-------------|
| **Framework** | React | 19 | Latest features, performance |
| **Language** | TypeScript | Latest | Type safety, refactoring |
| **Build Tool** | Vite | Latest | Fast HMR, optimized builds |
| **Styling** | TailwindCSS | Latest | Utility-first, responsive |
| **State** | React Query | Latest | Server state management |
| **Forms** | React Hook Form | Latest | Performance, validation |
| **Decimals** | decimal.js | Latest | Financial precision |
| **Charts** | Recharts | Latest | React-native charts |
| **Routing** | React Router | v6 | SPA routing |

### Infrastructure

| Componente | Tecnologia | Motivazione |
|-----------|-----------|-------------|
| **Containerization** | Docker | Consistency, portability |
| **Orchestration** | Docker Compose | Local dev, simple deploy |
| **CI/CD** | GitHub Actions | Native integration |
| **Testing Backend** | pytest | Python standard |
| **Testing Frontend** | Vitest | Vite-native, fast |
| **E2E Testing** | Playwright | Cross-browser, reliable |
| **Linting Backend** | Ruff | Fast, comprehensive |
| **Type Checking** | mypy | Static type validation |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards |
| **Logging** | structlog | Structured, traceable |

---

## 🛣️ Roadmap Implementazione

### Fase MVP - Ambiente Locale Single-User

**Obiettivo:** App funzionante localmente per 1 utente, no auth.

**Durata stimata:** 4-6 settimane

#### Milestone 1: Fondamenta (Settimana 1)

**Backend:**
- ✅ Setup Poetry + dipendenze complete
- ✅ Layer structure (api, services, repositories, domain)
- ✅ Value objects (Money, Percentage, PriceTarget)
- ✅ ApiResponse standard model
- ✅ Pydantic settings configuration
- ✅ Health check endpoint

**Frontend:**
- ✅ Setup Vite + React 19 + TypeScript
- ✅ TailwindCSS configuration
- ✅ Decimal.js wrapper
- ✅ Feature modules structure

**Infrastructure:**
- ✅ Docker Compose base (PostgreSQL + Redis)
- ✅ Database schema initial

#### Milestone 2: Core Domain (Settimana 2)

**Backend:**
- ✅ SQLAlchemy models (Ticker, Estimate, EstimateEvent, MarketData)
- ✅ Alembic migrations setup
- ✅ Repository pattern implementation
- ✅ EstimateService with business logic
- ✅ Event Sourcing per stime

**Database:**
- ✅ Materialized view EstimateSummaryView
- ✅ Indici ottimizzati per query frequenti

#### Milestone 3: API Layer (Settimana 3)

**Backend:**
- ✅ CRUD API Estimates
- ✅ API Market Data (prezzi real-time)
- ✅ MarketDataProvider abstraction
- ✅ Yahoo Finance provider implementation
- ✅ Redis caching per market data
- ✅ Rate limiting base

**Frontend:**
- ✅ API client centralizzato
- ✅ React Query setup
- ✅ Type definitions da OpenAPI

#### Milestone 4: UI Core (Settimana 4)

**Frontend:**
- ✅ Componenti shared (Button, Card, Input, Modal)
- ✅ EstimateList component
- ✅ EstimateDetail component
- ✅ CreateEstimateForm
- ✅ TickerSearch con autocomplete
- ✅ CloseEstimateModal

#### Milestone 5: Dashboard & Sync (Settimana 5)

**Frontend:**
- ✅ PortfolioDashboard
- ✅ PerformanceChart (Recharts)
- ✅ React Router setup
- ✅ Layout responsive

**Backend:**
- ✅ Google Drive API integration
- ✅ CSV parser per dati legacy v2.4
- ✅ SyncService bidirezionale
- ✅ Background worker (APScheduler)
- ✅ Script migrazione dati v2.4 → v3.0

#### Milestone 6: Testing & Docker (Settimana 6)

**Testing:**
- ✅ pytest setup + fixtures
- ✅ Unit tests value objects
- ✅ Unit tests EstimateService
- ✅ Integration tests API
- ✅ Vitest setup frontend
- ✅ Component tests EstimateForm

**Infrastructure:**
- ✅ Docker Compose dev (hot-reload)
- ✅ Dockerfile backend ottimizzato
- ✅ Dockerfile frontend (Nginx serve)
- ✅ README con istruzioni setup

---

### Fase 2 - Produzione Multi-User

**Obiettivo:** Deploy cloud con auth, osservabilità, sicurezza.

**Durata stimata:** 4-6 settimane

#### Milestone 7: Auth & Security (Settimana 7-8)

**Backend:**
- User model + RBAC (User, Role, Permission)
- JWT authentication
- Password hashing (bcrypt)
- OAuth2 flow
- Security middleware (CORS, CSP, XSS protection)
- Rate limiting avanzato (per user)
- Input validation completa
- Encryption at rest (sensitive data)

**Frontend:**
- Login/Register forms
- Protected routes
- Token management
- User profile page

#### Milestone 8: Observability (Settimana 9)

**Backend:**
- Structured logging (structlog)
- Correlation ID tracing
- Prometheus metrics
- Health checks completi
- Data quality monitor
- Data lineage tracking

**Infrastructure:**
- Grafana dashboards
- Alert rules
- Log aggregation

#### Milestone 9: Advanced Features (Settimana 10)

**Backend:**
- Outbox pattern per eventi
- Analytics API (aggregate queries)
- AI Prompt Service (Gemini integration)
- Feature flags
- Automated backup

**Frontend:**
- MarketDataChart con zoom
- TickerWatchlist management
- ChatAI component (Gemini)

#### Milestone 10: Testing Completo (Settimana 11)

**Testing:**
- Property-based testing (Hypothesis) per P&L
- E2E tests (Playwright) per tutti i flussi
- Chaos testing (resilienza)
- Load testing (Locust)
- Security testing (Bandit)

#### Milestone 11: CI/CD & Deploy (Settimana 12)

**CI/CD:**
- GitHub Actions pipeline completa
- Lint + test automatici
- Security scanning (Trivy)
- Coverage enforcement (80%+)
- Automated deploy staging
- Manual approval production

**Infrastructure:**
- Docker Compose production
- Multi-stage Dockerfiles
- SSL/TLS setup
- Secrets management
- Backup automatico
- Runbook operativo

**Documentation:**
- OpenAPI documentation completa
- Runbook troubleshooting
- Architecture decision records
- Developer onboarding guide

---

## 📐 Struttura Database

### Tabelle Core

#### `tickers`
```sql
CREATE TABLE tickers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255),
    sector VARCHAR(100),
    last_updated TIMESTAMP,
    metadata JSONB
);
```

#### `estimates`
```sql
CREATE TABLE estimates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker_id INTEGER REFERENCES tickers(id),
    direction VARCHAR(5) NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    entry_price DECIMAL(12,4) NOT NULL,
    entry_currency VARCHAR(3) DEFAULT 'USD',
    target_price DECIMAL(12,4) NOT NULL,
    target_percentage DECIMAL(8,4),
    stop_price DECIMAL(12,4) NOT NULL,
    stop_percentage DECIMAL(8,4),
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    opened_at TIMESTAMP NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP,
    exit_price DECIMAL(12,4),
    pnl_amount DECIMAL(12,4),
    pnl_percentage DECIMAL(8,4),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### `estimate_events`
```sql
CREATE TABLE estimate_events (
    id SERIAL PRIMARY KEY,
    estimate_id UUID REFERENCES estimates(id),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    occurred_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### `market_data`
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(id),
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    volume BIGINT,
    source VARCHAR(50) NOT NULL,
    UNIQUE(ticker_id, timestamp, source)
);
```

### Materialized Views

#### `estimate_summary_view`
```sql
CREATE MATERIALIZED VIEW estimate_summary_view AS
SELECT 
    t.symbol,
    e.direction,
    COUNT(*) as total_estimates,
    COUNT(*) FILTER (WHERE e.status = 'OPEN') as open_count,
    COUNT(*) FILTER (WHERE e.status = 'CLOSED') as closed_count,
    AVG(e.pnl_percentage) FILTER (WHERE e.status = 'CLOSED') as avg_pnl_pct,
    SUM(e.pnl_amount) FILTER (WHERE e.status = 'CLOSED') as total_pnl
FROM estimates e
JOIN tickers t ON e.ticker_id = t.id
GROUP BY t.symbol, e.direction;
```

---

## 🛡️ Sicurezza

### MVP (Base)

- ✅ HTTPS enforcement
- ✅ CORS configuration
- ✅ Rate limiting base (100 req/min)
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ XSS protection (CSP headers)

### Fase 2 (Produzione)

- JWT tokens con refresh
- Password hashing (bcrypt, cost=12)
- RBAC granulare
- Encryption at rest (AES-256)
- Audit logging completo
- Security headers completi
- Rate limiting per user
- IP whitelisting (opzionale)
- 2FA support (opzionale)

---

## 📊 Metriche & Monitoring

### Metriche Business

- Total estimates (open/closed)
- Win rate % (target hit / total closed)
- Average P&L per estimate
- Total P&L (cumulative)
- Best/worst performing tickers
- Average holding time

### Metriche Tecniche

- API response time (p50, p95, p99)
- Database query time
- Cache hit rate
- Background job success rate
- Error rate per endpoint
- Active users (Fase 2)

### Alerts

- API error rate > 5%
- Database connection pool exhausted
- Yahoo API failures
- Drive sync failures
- Disk usage > 80%
- Memory usage > 85%

---

## 📝 Best Practices

### Backend

1. **Usa SEMPRE `Decimal` per money** - Mai `float` per importi
2. **Repository pattern** - Separa persistence da business logic
3. **Service layer** - Business logic isolata da API
4. **Event Sourcing** - Ogni azione significativa genera evento
5. **Type hints** - Tutti i metodi tipizzati
6. **Docstrings** - Ogni public method documentato
7. **Unit tests** - Coverage minimo 80%
8. **Integration tests** - Tutti gli endpoint testati

### Frontend

1. **Usa SEMPRE `decimal.js`** - Mai `number` per calcoli finanziari
2. **API client centralizzato** - No `fetch` diretto
3. **Feature modules** - Isolamento componenti per feature
4. **Shared components** - Riusabilità UI
5. **Type safety** - Strict TypeScript
6. **React Query** - Server state management
7. **Error boundaries** - Gestione errori graceful
8. **Component tests** - Coverage componenti critici

### Git Workflow

1. **Branch naming**: `feature/TASK-X.Y-description`
2. **Commit message**: `feat(TASK-X.Y): description`
3. **PR template**: Task ID, checklist acceptance criteria
4. **Code review**: Almeno 1 approval
5. **CI passa**: Tutti i test green prima del merge

---

## 📜 Documentazione

### README principale
- Quick start (Docker one-command)
- Architecture overview
- Development setup
- Contributing guidelines

### API Documentation
- OpenAPI/Swagger auto-generated
- Request/response examples
- Error codes documentation
- Rate limiting info

### Runbook Operativo
- Startup/shutdown procedures
- Troubleshooting common issues
- Backup/restore procedures
- Scaling guidelines
- Monitoring dashboards

### ADR (Architecture Decision Records)
- Scelta DDD/CQRS/Event Sourcing
- Scelta PostgreSQL vs MongoDB
- Scelta React 19 vs Vue 3
- Scelta Decimal vs Float

---

## ✅ Acceptance Criteria Globali

### MVP Ready

- [ ] Tutti i 46 task MVP completati
- [ ] Coverage test backend ≥ 80%
- [ ] Coverage test frontend ≥ 70%
- [ ] Nessun errore critico in lint
- [ ] Nessuna dipendenza vulnerabile (Trivy)
- [ ] Docker Compose funziona con `docker compose up`
- [ ] Migrazione dati v2.4 → v3.0 verificata
- [ ] README con istruzioni chiare

### Production Ready (Fase 2)

- [ ] Tutti i 65 task completati
- [ ] Coverage test backend ≥ 85%
- [ ] Coverage test frontend ≥ 80%
- [ ] E2E tests per flussi critici
- [ ] Load testing superato (100 concurrent users)
- [ ] Security scan passed
- [ ] Backup automatico configurato
- [ ] Monitoring dashboards operativi
- [ ] Runbook operativo completo
- [ ] Documentazione API completa
- [ ] CI/CD pipeline funzionante

---

## 📞 Contatti & Support

**Project Owner:** Francesco Di Lecce  
**Repository:** https://github.com/Fradbari/TickerTracker

**Documentazione Tecnica:**
- AGENTS.md principale
- backend/AGENTS.md
- frontend/AGENTS.md
- Docker/AGENTS.md
- Docs/AGENTS.md

---

**Versione Piano:** 1.7  
**Último aggiornamento:** 31 Gennaio 2026  
**Prossima revisione:** Fine Fase MVP
