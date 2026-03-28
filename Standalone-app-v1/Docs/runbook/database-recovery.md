# Ripristino Database (Recovery)

Gli script di backup (`backup.py`) usano la crittografia (Fernet/AES).

## RTO Target: < 30 minuti

**Procedura di Restore:**
1. Recuperare l'ultimo backup cifrato.
2. Estrarre la chiave `BACKUP_ENCRYPTION_KEY`.
3. Decriptare il file. Esempio per AES (se si usa crittografia AES standard non Fernet python-specifica): `openssl enc -d -aes-256-cbc -in backup.enc -out database.sql`. Dal momento che la crittografia è Fernet in Python, si deve utilizzare uno script che richiami `cryptography.fernet`.
4. Procedere al restore: `pg_restore -c -U tt_user -d tickertracker -1 database.sql`