# Shared Domain - Value Objects

Questa directory contiene i **value objects immutabili** usati dal sistema. I value objects rappresentano concetti del dominio che non hanno identità propria (a differenza delle entità), ma sono definiti dal loro valore.

## Value Objects Implementati

### `Money` - Gestione Importi Monetari

**File**: `value_objects/money.py`

#### Descrizione
`Money` è un value object immutabile per gestire importi monetari con **precisione decimale garantita**. Evita gli errori di arrotondamento tipici dei float IEEE-754.

#### Caratteristiche Chiave

- **Immutabile** (frozen dataclass): Una volta creato, non può essere modificato
- **Type-safe**: Usa `Decimal` per tutti i calcoli, mai float
- **Validazione currency**: Richiede codici ISO 4217 (3 caratteri uppercase, es. "USD", "EUR")
- **Aritmetica sicura**: Somma/sottrazione tra valute diverse sollevano `ValueError`
- **Serializzazione round-trip**: Converte da/a dict preservando precisione

#### Utilizzo

```python
from decimal import Decimal
from src.shared.domain.value_objects import Money

# Creazione
money = Money(amount=Decimal("100.50"), currency="USD")
# o con conversione automatica
money = Money(amount=100.50, currency="EUR")  # int/float -> Decimal

# Aritmetica
m1 = Money(Decimal("100"), "USD")
m2 = Money(Decimal("50"), "USD")
result = m1 + m2  # Money(amount=150, currency="USD")
result = m1 - m2  # Money(amount=50, currency="USD")
result = m1 * 2   # Money(amount=200, currency="USD")
result = -m1      # Money(amount=-100, currency="USD")

# Arrotondamento (ROUND_HALF_UP)
money = Money(Decimal("10.125"), "USD")
rounded = money.round(places=2)  # Money(amount=10.13, currency="USD")

# Serializzazione
data = money.to_dict()  # {"amount": "10.13", "currency": "USD"}
restored = Money.from_dict(data)  # Money(amount=10.13, currency="USD")

# Stampa
print(money)  # "10.13 USD"
print(repr(money))  # Money(amount=Decimal('10.13'), currency='USD')
```

#### Validazioni

```python
# ✅ Valido
Money(Decimal("100"), "USD")
Money(100, "EUR")
Money("99.99", "GBP")

# ❌ Currency invalida
Money(Decimal("100"), "US")      # ValueError: troppo corta
Money(Decimal("100"), "usd")     # ValueError: non uppercase
Money(Decimal("100"), "USDA")    # ValueError: troppo lunga

# ❌ Amount invalido
Money("abc", "USD")              # decimal.InvalidOperation
```

#### Test Coverage

**36 test unitari** in `tests/unit/shared/domain/test_money.py`:

- ✅ Costruzione e validazione (11 test)
- ✅ Operazioni aritmetiche (14 test)
- ✅ Arrotondamento (4 test)
- ✅ Serializzazione/deserializzazione (6 test)
- ✅ Rappresentazione string (1 test)

Esegui i test:
```bash
make test-unit  # Oppure
python -m pytest tests/unit/shared/domain/test_money.py -v
```

#### Implementazione Accettata

- ✅ Classe immutabile (frozen dataclass)
- ✅ Tutti i calcoli usano Decimal, mai float
- ✅ Somma/sottrazione tra valute diverse solleva ValueError
- ✅ Moltiplicazione accetta solo Decimal o int
- ✅ Serializzazione/deserializzazione round-trip funziona
- ✅ Test unitari coprono tutti i metodi

---

### `Percentage` - Gestione Percentuali

**File**: `value_objects/percentage.py`

#### Descrizione
`Percentage` è un value object immutabile per gestire valori percentuali. Rappresenta le percentuali come frazioni decimali (es. 10% = 0.10).

#### Caratteristiche Chiave

- **Immutabile** (frozen dataclass): Una volta creato, non può essere modificato
- **Decimal-based**: Usa sempre `Decimal` per precisione
- **Conversione basis points**: Factory method `from_basis_points()` per convertire da bps
- **Applicazione a Money**: Metodo `apply_to(money)` per calcolare percentuali su importi
- **Moltiplicatore**: Metodo `as_multiplier()` per uso diretto in calcoli (es. 10% → 1.10)
- **Aritmetica**: Somma/sottrazione tra percentuali

#### Utilizzo

```python
from decimal import Decimal
from src.shared.domain.value_objects import Percentage, Money

# Creazione diretta (10% = 0.10)
pct = Percentage(value=Decimal("0.10"))

# Creazione da basis points (100 bps = 1% = 0.01)
pct = Percentage.from_basis_points(1000)  # 10%

# Applicare percentuale a Money
money = Money(Decimal("100"), "USD")
result = pct.apply_to(money)  # Money(Decimal("110"), "USD")

# Usare come moltiplicatore
multiplier = pct.as_multiplier()  # Decimal("1.10")
adjusted = Decimal("100") * multiplier  # Decimal("110")

# Aritmetica tra percentuali
pct1 = Percentage(value=Decimal("0.10"))
pct2 = Percentage(value=Decimal("0.05"))
combined = pct1 + pct2  # Percentage(value=Decimal("0.15"))

# Serializzazione
data = pct.to_dict()  # {"value": "0.10"}
restored = Percentage.from_dict(data)  # Percentage(value=Decimal("0.10"))

# Stampa
print(pct)  # "10.00%"
print(repr(pct))  # Percentage(value=Decimal('0.10'))
```

#### Basis Points

I basis points (bps) sono una unità standard in finanza:
- 100 bps = 1% = 0.01
- 50 bps = 0.5% = 0.005
- 1 bps = 0.01% = 0.0001

```python
pct = Percentage.from_basis_points(250)  # 2.5%
assert pct.value == Decimal("0.025")
```

#### Test Coverage

**39 test unitari** in `tests/unit/shared/domain/test_percentage.py`:

- ✅ Costruzione e validazione (6 test)
- ✅ Conversione basis points (7 test)
- ✅ Applicazione a Money (5 test)
- ✅ Moltiplicatori (4 test)
- ✅ Operazioni aritmetiche (5 test)
- ✅ Serializzazione (5 test)
- ✅ String representation (4 test)
- ✅ Integration tests (3 test)

Esegui i test:
```bash
python -m pytest tests/unit/shared/domain/test_percentage.py -v
```

#### Implementazione Accettata

- ✅ Classe immutabile (frozen dataclass)
- ✅ Conversione da basis points corretta (100 bps = 1%)
- ✅ `apply_to` restituisce Money con importo corretto
- ✅ `as_multiplier` per 10% restituisce Decimal("1.10")
- ✅ Test unitari coprono tutti i metodi

---

## Summary Test Coverage

**75 test passanti totali** ✨:
- Money: 36 test
- Percentage: 39 test

## Estensioni Future

### Prossimi Value Objects (Planned)

- `Price`: Prezzo di un asset con timestamp
- `Percentage`: Percentuale con validazione 0-100
- `Quantity`: Quantità di azioni (non negativa)
- `TimeFrame`: Intervallo di tempo (1D, 1H, 5M, etc.)
- `TradeStatus`: Enum per stati trade (PENDING, EXECUTED, CANCELLED)

## Design Patterns

### Immutabilità

I value objects sono immutabili per:
1. **Predictability**: Nessun side effect durante l'uso
2. **Thread-safety**: Sicuri in ambienti multithreading
3. **Hashability**: Potenzialmente hashable per uso in set/dict (future)

### Operazioni Defensive

Tutte le operazioni aritmetiche restituiscono **nuove istanze** (non mutano l'originale):

```python
original = Money(Decimal("100"), "USD")
result = original + Money(Decimal("50"), "USD")
# original rimane immutato: Money(Decimal("100"), "USD")
# result è una nuova istanza: Money(Decimal("150"), "USD")
```

### Validazione Rigorosa

La validazione avviene in `__post_init__()` per garantire che **solo istanze valide esistono** nel sistema.

## Riferimenti

- [Decimal Python Docs](https://docs.python.org/3/library/decimal.html)
- [Pydantic Field Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Domain-Driven Design: Value Objects](https://martinfowler.com/bliki/ValueObject.html)
