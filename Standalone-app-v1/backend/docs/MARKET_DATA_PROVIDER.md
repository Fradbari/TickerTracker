# MarketDataProvider Architecture

## Overview

Il MarketDataProvider è un'astrazione che disaccoppia la logica di business dalle specifiche fonti di dati di mercato (Yahoo Finance, Finnhub, Alpha Vantage, etc.).

## Design Pattern

Il sistema implementa il **Strategy Pattern** combinato con **Dependency Injection** per permettere:

- **Testabilità**: FakeProvider per test deterministici senza chiamate esterne
- **Flessibilità**: Cambio provider senza modificare business logic
- **Estensibilità**: Aggiunta di nuovi provider senza impatto su codice esistente
- **Configuration**: Provider selezionabile via configurazione/ambiente

## Provider Interface

```python
class MarketDataProvider(ABC):
    """Interfaccia astratta per provider di dati di mercato."""
    
    @abstractmethod
    async def get_current_price(self, symbol: str) -> PriceData:
        """Ottiene il prezzo corrente per un simbolo."""
        pass
    
    @abstractmethod
    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str = "1d",
    ) -> List[PriceData]:
        """Ottiene lo storico prezzi per un periodo."""
        pass
    
    @abstractmethod
    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        """Ottiene dati fondamentali (P/E, market cap, etc.)."""
        pass
    
    @abstractmethod
    async def search_symbol(self, query: str) -> List[dict]:
        """Cerca simboli ticker."""
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identificatore della fonte dati."""
        pass
    
    @property
    @abstractmethod
    def supports_realtime(self) -> bool:
        """Indica se i dati sono real-time o ritardati."""
        pass
```

## Data Contracts

### PriceData

Contratto standardizzato per dati OHLCV:

```python
class PriceData(BaseModel):
    symbol: str                      # Ticker symbol
    date: DateType                   # Data del dato
    open: Decimal                    # Prezzo apertura
    high: Decimal                    # Prezzo massimo
    low: Decimal                     # Prezzo minimo
    close: Decimal                   # Prezzo chiusura
    volume: int                      # Volume scambiato
    adjusted_close: Optional[Decimal]  # Chiusura aggiustata
    source: str                      # Provider origine
    timestamp: datetime              # Quando recuperato
```

### FundamentalsData

Dati fondamentali azienda:

```python
class FundamentalsData(BaseModel):
    symbol: str
    company_name: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[Decimal]
    pe_ratio: Optional[Decimal]      # Price/Earnings
    eps: Optional[Decimal]           # Earnings per share
    dividend_yield: Optional[Decimal]
    beta: Optional[Decimal]
    fifty_two_week_high: Optional[Decimal]
    fifty_two_week_low: Optional[Decimal]
    average_volume: Optional[int]
    source: str
    timestamp: datetime
```

## Implementazioni Provider

### YahooMarketDataProvider ✅

Provider principale per dati di mercato gratuiti e affidabili.

**Caratteristiche:**
- Dati ritardati di 15-20 minuti (non real-time)
- Storico disponibile fino a decenni fa
- Copertura globale (NYSE, NASDAQ, LSE, etc.)
- Dati fondamentali disponibili
- Nessuna API key richiesta
- Gratuito senza limiti stringenti

**Implementazione:**
```python
provider = YahooMarketDataProvider(timeout=30)
price = await provider.get_current_price("AAPL")
```

**File:** `src/market_data/services/yahoo_provider.py`

### FakeMarketDataProvider ✅

Provider per testing e sviluppo.

**Caratteristiche:**
- Dati configurabili manualmente
- Simulazione errori per test
- Nessuna chiamata esterna
- Deterministico e veloce

**Utilizzo nei test:**
```python
# Setup
provider = FakeMarketDataProvider()
provider.set_price("AAPL", Decimal("150.00"))
provider.set_fundamentals("AAPL", custom_fundamentals)

# Test
price = await provider.get_current_price("AAPL")
assert price.close == Decimal("150.00")

# Simulazione errore
provider.fail_on_symbol("FAIL")
await provider.get_current_price("FAIL")  # Raises DataUnavailableError
```

**File:** `src/market_data/services/provider_implementations.py`

### FinnhubMarketDataProvider ⏸️ (Stub)

Provider per dati real-time con piano gratuito.

**Caratteristiche:**
- ✅ Real-time data per US markets
- ✅ Free tier: 60 chiamate/minuto
- ✅ Websocket per streaming
- ✅ News e sentiment analysis

**Status:** Stub implementato, richiede implementazione completa.

**TODO:**
```bash
pip install finnhub-python
# Implementare in src/market_data/services/finnhub_provider.py
```

### AlphaVantageMarketDataProvider ⏸️ (Stub)

Provider con indicatori tecnici inclusi.

**Caratteristiche:**
- ✅ Dati real-time e storici
- ✅ Indicatori tecnici pre-calcolati
- ✅ Cripto e forex
- ⚠️ Free tier: 5 chiamate/minuto, 500/giorno

**Status:** Stub implementato, richiede implementazione completa.

### PolygonMarketDataProvider ⏸️ (Stub)

Provider enterprise con qualità dati molto alta.

**Caratteristiche:**
- ✅ Dati tick-by-tick disponibili
- ✅ Opzioni e cripto
- ✅ Qualità dati eccellente
- ⚠️ Free tier: dati ritardati

**Status:** Stub implementato, richiede implementazione completa.

## MarketDataService

Service che orchestra l'uso del provider con repository per persistenza.

```python
class MarketDataService:
    def __init__(
        self,
        provider: MarketDataProvider,  # ← Dependency injection
        repository: MarketDataRepository,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self._provider = provider
        self._repository = repository
        self._session_factory = session_factory
    
    async def get_current_price(self, ticker_id: UUID) -> Decimal:
        """
        Ottiene prezzo corrente.
        1. Prova dal repository (cache database)
        2. Se non disponibile, chiama provider
        3. Salva in repository per uso futuro
        """
        # Implementazione...
    
    async def sync_historical_data(
        self,
        ticker_id: UUID,
        start_date: date,
        end_date: date,
    ) -> int:
        """
        Sincronizza dati storici da provider a repository.
        Returns: numero di righe sincronizzate.
        """
        # Implementazione...
```

## Dependency Injection in FastAPI

```python
from fastapi import Depends
from src.market_data.services import YahooMarketDataProvider, MarketDataService

async def get_market_data_provider() -> MarketDataProvider:
    """Factory per provider corrente."""
    # Configurabile via environment
    return YahooMarketDataProvider(timeout=30)

async def get_market_data_service(
    provider: MarketDataProvider = Depends(get_market_data_provider),
    repository: MarketDataRepository = Depends(get_repository),
) -> MarketDataService:
    """Factory per service con dipendenze iniettate."""
    return MarketDataService(provider, repository, AsyncSessionLocal)

@router.get("/tickers/{ticker_id}/price")
async def get_ticker_price(
    ticker_id: UUID,
    service: MarketDataService = Depends(get_market_data_service),
):
    price = await service.get_current_price(ticker_id)
    return success_response({"price": str(price)})
```

## Exception Handling

Il provider solleva eccezioni tipizzate per gestione errori consistente:

```python
from src.market_data.domain.providers import (
    SymbolNotFoundError,
    DataUnavailableError,
    RateLimitExceededError,
)

try:
    price = await provider.get_current_price("INVALID")
except SymbolNotFoundError as e:
    # Simbolo non trovato
    return error_response("SYMBOL_NOT_FOUND", str(e))
except DataUnavailableError as e:
    # Servizio temporaneamente non disponibile
    return error_response("DATA_UNAVAILABLE", str(e))
except RateLimitExceededError as e:
    # Rate limit raggiunto
    retry_after = e.retry_after
    return error_response("RATE_LIMIT", str(e))
```

## Testing

### Unit Test con FakeProvider

```python
async def test_service_uses_provider():
    # Arrange
    fake_provider = FakeMarketDataProvider()
    fake_provider.set_price("AAPL", Decimal("150.00"))
    
    service = MarketDataService(
        provider=fake_provider,
        repository=mock_repository,
        session_factory=mock_factory,
    )
    
    # Act
    price = await service.get_current_price(ticker_id)
    
    # Assert
    assert price == Decimal("150.00")
```

### Integration Test con YahooProvider

```python
@pytest.mark.integration
async def test_yahoo_provider_real_data():
    provider = YahooMarketDataProvider()
    
    price_data = await provider.get_current_price("AAPL")
    
    assert price_data.symbol == "AAPL"
    assert price_data.close > 0
    assert price_data.source == "yahoo"
```

## Future Enhancements

### TASK 2.19: Caching & Backoff

Prossimo task per aggiungere:

- **Cache TTL-based**: Ridurre chiamate esterne
  - Prezzi correnti: 60s TTL
  - Storico: 1h TTL
  - Fundamentals: 24h TTL

- **Retry con backoff**: Gestione resiliente errori
  - Timeout automatico
  - Retry esponenziale
  - Fallback a dati cache "stale"

- **CachedMarketDataProvider**: Wrapper decoratore per ogni provider

## File Structure

```
backend/src/market_data/
├── domain/
│   ├── providers.py                    # ✅ Interfaccia astratta + Data contracts
│   ├── entities.py                     # Ticker entity
│   └── market_data.py                  # MarketData entity
├── services/
│   ├── yahoo_provider.py               # ✅ Yahoo Finance implementation
│   ├── provider_implementations.py     # ✅ Fake + Stubs (Finnhub, AV, Polygon)
│   └── market_data_service.py          # ✅ Service con DI del provider
├── repositories/
│   └── market_data_repository.py       # Database access
└── api/
    └── routes.py                        # (TODO) REST endpoints

tests/
└── test_market_data_provider.py        # ✅ Unit test suite (5/5 passed)
```

## References

- Provider Interface: [src/market_data/domain/providers.py](../src/market_data/domain/providers.py)
- Yahoo Implementation: [src/market_data/services/yahoo_provider.py](../src/market_data/services/yahoo_provider.py)
- Test Suite: [tests/test_market_data_provider.py](../tests/test_market_data_provider.py)
- AGENTS.md: Task 2.18 completion status
