# `shared` - Shared/Cross-Cutting Concerns Layer

This module contains code shared across all bounded contexts: value objects, domain models, infrastructure utilities, and schemas that are applicable across multiple domains.

## Directory Structure

```
shared/
├── domain/               # Shared domain models and value objects
│   ├── value_objects/    # Immutable value objects (Money, Percentage, PriceTarget)
│   └── README.md         # Detailed documentation on value objects
├── infra/                # Infrastructure layer (configuration, caching, logging)
│   ├── config.py         # Multi-environment configuration with Pydantic Settings
│   ├── cache/            # Caching layer (future)
│   ├── drive/            # Google Drive integration (future)
│   ├── logging/          # Structured logging setup (future)
│   ├── security/         # Encryption and security utilities (future)
│   ├── yahoo/            # Yahoo Finance API integration (future)
│   └── README.md         # Infrastructure documentation
├── api/                  # Shared API utilities (future)
├── schemas/              # Shared Pydantic schemas (future)
├── repositories/         # Base repository patterns (future)
└── services/             # Cross-cutting services (future)
```

## Key Components

### 1. Domain Layer (`domain/`)

**Value Objects**:
- **`Money`** (36 tests): Immutable decimal-safe monetary value object
  - Handles currency validation (ISO 4217)
  - All arithmetic operations (add, subtract, multiply)
  - Proper rounding with ROUND_HALF_UP
  - Serialization with precision preservation

- **`Percentage`** (39 tests): Immutable percentage value object
  - Basis points conversion (100 bps = 1%)
  - Money application with precision
  - Multiplier calculation for direct use
  - Arithmetic between percentages

- **`PriceTarget`** (41 tests): Directional trade target with validation
  - LONG/SHORT validation rules
  - Risk/reward ratio calculation
  - Target/stop hit detection
  - Full serialization support

### 2. Infrastructure Layer (`infra/`)

**Configuration Management**:
- **`config.py`** (27 tests): Pydantic Settings for multi-environment configuration
  - Environment-specific values (local/staging/production)
  - Secret protection with SecretStr for all sensitive data
  - Environment variable loading with .env file support
  - Singleton pattern with `get_settings()` function
  - Full validation for all fields

## Test Coverage Summary

**Total Tests**: 143 passing ✅

| Component | Tests | Status |
|-----------|-------|--------|
| Money | 36 | ✅ Passing |
| Percentage | 39 | ✅ Passing |
| PriceTarget | 41 | ✅ Passing |
| Configuration | 27 | ✅ Passing |
| **TOTAL** | **143** | **✅ All Green** |

## Usage Examples

### Using Value Objects

```python
from src.shared.domain import Money, Percentage, PriceTarget

# Create money values
entry_price = Money("100.50", "USD")
target_price = Money("110.00", "USD")

# Apply percentage to money
fee_pct = Percentage("0.025")  # 2.5%
fee_amount = fee_pct.apply_to(entry_price)

# Create price target for LONG trade
pt = PriceTarget(
    entry_price=entry_price,
    stop_loss=Money("95.00", "USD"),
    take_profit=target_price,
    direction="LONG"
)

# Check if target is hit
if pt.is_target_hit(Money("110.50", "USD")):
    print("Take profit reached!")

# Calculate risk/reward ratio
ratio = pt.risk_reward_ratio()  # Returns Decimal
```

### Using Configuration

```python
from src.shared.infra.config import get_settings

# Get application settings (cached singleton)
settings = get_settings()

# Access environment-specific configuration
if settings.DEBUG:
    print(f"Running in {settings.ENVIRONMENT} with log level {settings.LOG_LEVEL}")

# Access secrets safely
db_url = settings.DATABASE_URL.get_secret_value()
api_key = settings.GEMINI_API_KEY.get_secret_value()
```

## Design Principles

1. **Immutability**: All value objects are frozen dataclasses, preventing accidental mutations
2. **Type Safety**: Full type hints with Literal types for enums (LONG/SHORT)
3. **Validation**: Fail-fast validation in constructors ensures only valid instances exist
4. **Security**: All sensitive values use SecretStr and are properly masked in logs
5. **Precision**: Decimal arithmetic throughout (never float) for financial calculations
6. **Serialization**: All value objects support round-trip dict conversion

## Dependencies

- **pydantic** (2.5.3+): For validation and SecretStr
- **pydantic-settings** (2.1.0+): For multi-environment configuration
- **python-dotenv** (1.0.0+): For .env file loading
- Standard library: dataclasses, decimal, typing, functools

## Next Steps

- [ ] Implement `api/` layer with shared API response models
- [ ] Implement `schemas/` with common Pydantic schemas
- [ ] Implement `repositories/` with base repository patterns
- [ ] Implement `services/` with cross-cutting services
