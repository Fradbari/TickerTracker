# Sync Infrastructure Module

Modulo infrastrutturale per la sincronizzazione con Google Drive e gestione del formato CSV legacy di TickerTracker.

## Componenti

### 1. Legacy Models (`legacy_models.py`)

Dataclasses che rappresentano le righe CSV del formato legacy:

- **`LegacyEstimateRow`**: 70+ campi per estimates (ticker, prezzi, fundamentals, indicators, metadata)
- **`LegacyHistoryRow`**: 8 campi per storico market data (OHLCV + Date + Ticker)

Entrambe forniscono metodo `to_dict()` per conversione CSV-compatible.

### 2. CSV Parser (`csv_parser.py`)

Parser bidirezionale per formato CSV legacy con 120+ colonne:

#### Metodi Principali

**Parsing:**
- `parse_estimates_csv(content: bytes) -> List[LegacyEstimateRow]`
- `parse_history_csv(content: bytes) -> List[LegacyHistoryRow]`

**Export:**
- `export_estimate_to_csv_row(estimate: Estimate, fundamentals: dict) -> str`
- `export_history_to_csv(data: List[MarketData]) -> bytes`

#### Caratteristiche
- ✅ UTF-8 con BOM (Excel compatible)
- ✅ Safe type conversion (Decimal, int, date, datetime)
- ✅ Gestione colonne mancanti con default sensati
- ✅ Error handling robusto con logging
- ✅ Round-trip validation

### 3. Column Mapping (`COLUMN_MAPPING.md`)

Documentazione completa del mapping colonne legacy → campi interni:
- 120+ colonne estimates (ticker, prezzi, fundamentals, indicators, metadata)
- 7-8 colonne history (OHLCV)
- Encoding notes, date formats, error handling

## Utilizzo

### Parse Estimates CSV

```python
from src.sync.infra.csv_parser import LegacyCsvParser

parser = LegacyCsvParser()

with open('estimates.csv', 'rb') as f:
    content = f.read()

estimates = parser.parse_estimates_csv(content)

for est in estimates:
    print(f"{est.ticker}: {est.status} - Target: {est.target_price}")
```

### Export Estimate to CSV

```python
from src.sync.infra.csv_parser import LegacyCsvParser

parser = LegacyCsvParser()
estimate = ...  # Estimate entity

csv_row = parser.export_estimate_to_csv_row(estimate, fundamentals={})

with open('estimates.csv', 'a', encoding='utf-8-sig') as f:
    f.write(csv_row + '\n')
```

### Parse History CSV

```python
from src.sync.infra.csv_parser import LegacyCsvParser

parser = LegacyCsvParser()

with open('History_AAPL.csv', 'rb') as f:
    content = f.read()

history = parser.parse_history_csv(content)

for row in history:
    print(f"{row.date}: Close={row.close}, Volume={row.volume}")
```

### Export History to CSV

```python
from src.sync.infra.csv_parser import LegacyCsvParser

parser = LegacyCsvParser()
market_data = [...]  # List[MarketData]

csv_bytes = parser.export_history_to_csv(market_data)

with open('History_AAPL.csv', 'wb') as f:
    f.write(csv_bytes)
```

## Testing

Il modulo è completamente testato con 30 test che coprono:
- Safe type conversions (14 tests)
- Parsing estimates (5 tests)
- Export estimates (1 test)
- Parsing history (3 tests)
- Export history (2 tests)
- Round-trip validation (2 tests)
- Edge cases (3 tests)

```bash
pytest tests/sync/test_csv_parser.py -v
```

**Risultati:** ✅ 30/30 test passati (100%)

## Architettura

```
src/sync/infra/
├── __init__.py                 # Package marker
├── legacy_models.py            # Dataclasses per formato legacy (~170 lines)
├── csv_parser.py               # Parser bidirezionale (~650 lines)
├── COLUMN_MAPPING.md           # Documentazione mapping colonne (~200 lines)
└── README.md                   # Questo file
```

## Integrazione

Questo modulo è utilizzato da:
- **SyncService** (TASK 2.22): Coordina sincronizzazione DB ↔ Google Drive
- **Google Drive Client** (TASK 2.20): Upload/download file CSV

Dipende da:
- `src.estimates.domain.entities.Estimate`: Modello estimate
- `src.market_data.domain.market_data.MarketData`: Modello market data

## Design Decisions

### Perché Dataclasses?
- Type safety con type hints
- Immutabilità dei dati
- Metodi built-in (__repr__, __eq__, etc.)
- Leggibilità e manutenibilità

### Perché csv.DictReader?
- Accesso per nome colonna (più robusto di indice)
- Gestisce header automaticamente
- Tollerante a variazioni nell'ordine colonne

### Perché UTF-8-sig?
- Compatibilità con Excel su Windows
- BOM (Byte Order Mark) previene problemi di encoding
- Standard su piattaforma legacy

## Limitazioni Note

- **No streaming export**: Export carica tutto in memoria (acceptable per < 10k righe)
- **Single-threaded**: Non parallelo (CSV non si presta a parallelizzazione)
- **No compression**: Output plain CSV (compressione gestita a livello Drive)

## Future Enhancements (Opzionale)

- [ ] Supporto per CSV compresso (gzip)
- [ ] Streaming export per dataset molto grandi
- [ ] Validazione schema con pydantic
- [ ] Auto-detection encoding per file senza BOM

## Documentation

Per dettagli completi:
- Column mapping: [COLUMN_MAPPING.md](./COLUMN_MAPPING.md)
- Completion report: [archivio completion logs](../../../docs/history/TASK-COMPLETION-LOGS.md)
- AGENTS tasks: [AGENTS.md](../AGENTS.md)

---

**Versione:** 1.0  
**Status:** ✅ Production Ready  
**Test Coverage:** 100% (30/30 tests passing)
