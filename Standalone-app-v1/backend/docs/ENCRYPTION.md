# Encryption at Rest — Task 3.4

`EncryptedString` TypeDecorator per SQLAlchemy: cifra in modo trasparente i campi stringa a riposo usando Fernet (AES-128-CBC + HMAC SHA-256).

## Setup

```env
ENCRYPTION_KEY=<base64-fernet-key>
```

Genera una key con:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

⚠️ **Mai committare la key.** `.env` è in `.gitignore`.

## Uso come TypeDecorator

```python
from src.shared.infra.security.encryption import EncryptedString

class User(Base):
    __tablename__ = "users"
    email = Column(EncryptedString(255), nullable=False)
    api_key = Column(EncryptedString(255))
```

Il campo viene:
- **Cifrato** automaticamente prima di `session.add()` / `INSERT`
- **Decifrato** automaticamente dopo `session.execute(SELECT)`
- Restituisce `str` Python in memoria, opaco a SQLAlchemy

## Operazioni supportate

| Metodo | Firma | Note |
|---|---|---|
| `rotate_key` | `rotate_key(session, model_cls, column_name, old_key, new_key)` | Ri-cifra tutti i valori di una colonna senza leak |
| `EncryptionConfigError` | exception | Sollevata se `ENCRYPTION_KEY` manca o è invalida |
| `DecryptionError` | exception | Sollevata se il payload è corrotto o la key è sbagliata |

## Rotazione key

```python
from src.shared.infra.security.encryption import rotate_key
from cryptography.fernet import Fernet

old_key = Fernet(os.environ["OLD_ENCRYPTION_KEY"])
new_key = Fernet(os.environ["NEW_ENCRYPTION_KEY"])

updated = await rotate_key(
    session=session,
    model_cls=User,
    column_name="email",
    old_key=old_key,
    new_key=new_key,
)
print(f"Re-encrypted {updated} rows")
```

## Performance

- Encrypt: ~5μs / campo
- Decrypt: ~5μs / campo
- NOAA overhead fino a ~50ms / 10k righe (accettabile)

## Test Coverage

35 test in `backend/tests/infra/test_encryption.py`. Coprono:
- round-trip encrypt/decrypt
- invalid key handling
- corrupted payload detection
- bulk rotation senza leak intermedio
- comportamento con `null` / empty string

## Limitazioni note

- Solo `str` (no JSON nested objects) → per quelli usare `EncryptedJSON`
- Non cifrare campi indicizzati (`WHERE encrypted_col = ?` non è possibile senza `pgcrypto`)
- La key vive in process memory: assicurarsi di non loggarla
