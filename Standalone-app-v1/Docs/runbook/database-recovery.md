# Ripristino Database (Recovery)

**RTO: < 30 min | RPO: 24h (Ultimo backup giornaliero)**

Gli script di backup (`backup.py`) usano la crittografia (Fernet Python library).

## Procedura di Restore:
1. Recuperare l'ultimo backup cifrato.
2. Assicurarsi di avere la variabile d'ambiente `BACKUP_ENCRYPTION_KEY` impostata.
3. Decriptare il file utilizzando uno script Python `cryptography` direttamente dall'host o da un ambiente isolato:

```python
# decripta_backup.py
import sys
import os
from cryptography.fernet import Fernet

key = os.getenv("BACKUP_ENCRYPTION_KEY").encode()
f = Fernet(key)

with open("backup.enc", "rb") as enc, open("backup.sql", "wb") as out:
    out.write(f.decrypt(enc.read()))
```
Esegui: `python decripta_backup.py`

4. Ottenuto `backup.sql`, muoversi nella radice del progetto e rigenerare il DB:

```bash
cd Standalone-app-v1/
docker compose -f docker-compose.prod.yml exec -T db pg_restore -c -U tt_prod_user -d tickertracker_prod < backup.sql
```

## Contatti ed Escalation
Per assistenza tecnica al database, fare riferimento ai DB Admin o DevOps su [CONTACTS.md](CONTACTS.md).
