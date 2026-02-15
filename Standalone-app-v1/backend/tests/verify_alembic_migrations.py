import subprocess
import sys
from datetime import datetime

ALEMBIC_CMD = [sys.executable, '-m', 'alembic']


def run_alembic_cmd(args):
    result = subprocess.run(
        ALEMBIC_CMD + args,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Errore comando alembic {' '.join(args)}:\n{result.stderr}")
        sys.exit(1)
    return result.stdout


def get_current_revision():
    output = run_alembic_cmd(['current'])
    print("\n== Stato migrazioni Alembic (HEAD) ==")
    print(output.strip())
    return output


def list_all_migrations():
    output = run_alembic_cmd(['history', '--verbose'])
    print("\n== Lista tutte le migrazioni applicate ==")
    lines = output.splitlines()
    migrations = []
    rev, date, msg = None, None, None
    for line in lines:
        if line.strip().startswith('Rev:'):
            rev = line.split(':', 1)[1].strip()
        elif line.strip().startswith('Revision ID:'):
            rev = line.split(':', 1)[1].strip()
        elif line.strip().startswith('Create Date:'):
            date = line.split(':', 1)[1].strip()
        elif line.strip().startswith('Message:') or line.strip().startswith('    '):
            # Try to extract message from indented lines or Message:
            if 'Message:' in line:
                msg = line.split(':', 1)[1].strip()
            elif rev and not msg and line.strip():
                msg = line.strip()
        if rev and date and msg:
            migrations.append({'rev': rev, 'date': date, 'msg': msg})
            rev, date, msg = None, None, None
    # Fallback: if no msg, just print rev and date
    for m in migrations:
        print(f"{m['rev']} | {m.get('date','')} | {m.get('msg','')}")
    return migrations


def check_last_migration(migrations):
    print("\n== Verifica ultima migrazione ==")
    if not migrations:
        print("❌ Nessuna migrazione trovata!")
        sys.exit(1)
    last = migrations[0]  # history --verbose is in reverse order (latest first)
    if 'add_outbox_pattern_fields' in last['msg'] or 'outbox_pattern' in last['rev']:
        print(f"✅ Ultima migrazione: {last['msg']} ({last['rev']})")
    else:
        print(f"❌ Ultima migrazione non è 'add_outbox_pattern_fields': {last['msg']} ({last['rev']})")
        sys.exit(1)


def check_indices():
    import sqlalchemy as sa
    from src.shared.infra.config import get_settings
    from src.shared.infra.database import engine
    print("\n== Verifica indici ==")
    insp = sa.inspect(engine)
    indices = insp.get_indexes('estimate_events')
    found_ix1 = any(ix['name'] == 'ix_estimate_events_unprocessed' for ix in indices)
    found_ix2 = any(ix['name'] == 'ix_estimate_event_timeline' for ix in indices)
    if found_ix1:
        print("✅ Indice ix_estimate_events_unprocessed presente")
    else:
        print("❌ Indice ix_estimate_events_unprocessed mancante")
    if found_ix2:
        print("✅ Indice ix_estimate_event_timeline presente")
    else:
        print("❌ Indice ix_estimate_event_timeline mancante")
    if not (found_ix1 and found_ix2):
        sys.exit(1)


def main():
    get_current_revision()
    migrations = list_all_migrations()
    check_last_migration(migrations)
    check_indices()
    print("\n== Verifica migrazioni Alembic completata ==")

if __name__ == "__main__":
    main()
