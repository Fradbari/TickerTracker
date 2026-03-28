# Ripristino Database (Recovery)

Gli script di backup (`backup.py`) usano la crittografia (Fernet/AES).

## RTO Target: < 30 minuti

**Procedura di Restore:**
1. Recuperare l'ultimo backup cifrato.
2. Assicurarsi di avere la variabile d'ambiente `BACKUP_ENCRYPTION_KEY` impostata correttamente.
3. Decriptare il file utilizzando uno script Python basato sulla libreria `cryptography` (la stessa utilizzata in fase di backup), poiché la CLI OpenSSL originariamente suggerita non risolve la logica di crittografia Fernet:

```python
# decripta_backup.py
import sys
from cryptography.fernet import Fernet

key = b"<LA_TUA_BACKUP_ENCRYPTION_KEY>"
f = Fernet(key)

with open("backup.enc", "rb") as enc, open("backup.sql", "wb") as out:
    out.write(f.decrypt(enc.read()))
```
Esegui: `python decripta_backup.py`

4. Una volta ottenuto `backup.sql`, procedere con la rigenerazione nel database primario PostgreSQL lanciando il comando dall'host:

```bash
docker exec -i tickertracker-db-prod pg_restore -c -U tt_prod_user -d tickertracker_prod < backup.sql
```