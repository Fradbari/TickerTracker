# Input Validation — Task 3.3

Validatori centralizzati in `src/shared/schemas/validators.py`. **63 test** coprono edge case unicode, injection, lang range.

## Validatori disponibili

| Validator | Input | Output | Garantisce |
|---|---|---|---|
| `sanitize_ticker` | `str` | `str` | `[A-Z0-9.\-_]{1,12}`, uppercase, no injection chars |
| `sanitize_text` | `str` | `str` | strip tag HTML/script, length ≤ N, trim |
| `validate_price` | `Decimal \| str` | `Decimal` | positivo, ≤ `MAX_PRICE`, scale 4 cifre decimali |
| `validate_percentage` | `Decimal \| str` | `Decimal` | -100..1000, scale 4 cifre |
| `validate_date_range` | tuple `date` | `tuple` | `start <= end`, entrambe non future > N giorni |

## Esempio

```python
from src.shared.schemas.validators import (
    sanitize_ticker, validate_price, validate_percentage
)
from decimal import Decimal

ticker = sanitize_ticker("aapl")           # "AAPL"
price = validate_price("100.50")           # Decimal("100.50")
pct = validate_percentage("15.5")          # Decimal("15.5")
```

## Note architetturali

- Validators sollevano `ValueError` con messaggio strutturato (`code: "INVALID_TICKER"`)
- Sono integrati con `ApiResponse` error wrapper via middleware `ErrorHandler`
- I validator **NON** lavorano su body JSON direttamente: passano per gli schemi Pydantic, poi le funzioni di sanitizzazione sono applicate in `services/`

## Test Coverage

63 test in `backend/tests/shared/test_validators.py` (Task 3.3).

## File chiave

`backend/src/shared/schemas/validators.py`
