import sys

from alembic.config import Config
from alembic.script import ScriptDirectory


def get_alembic_config():
    # Path to alembic.ini in backend dir
    cfg = Config("alembic.ini")
    return cfg

def get_current_revision():
    cfg = get_alembic_config()
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    print("\n== Stato migrazioni Alembic (HEAD) ==")
    for head in heads:
        rev = script.get_revision(head)
        print(f"{rev.revision} (head) | {rev.doc or ''}")
    return heads

def list_all_migrations():
    cfg = get_alembic_config()
    script = ScriptDirectory.from_config(cfg)
    print("\n== Lista tutte le migrazioni applicate ==")
    migrations = []
    for rev in script.walk_revisions():
        # walk_revisions yields from newest to oldest
        migrations.append({
            'rev': rev.revision,
            'date': getattr(rev, 'create_date', ''),
            'msg': rev.doc or ''
        })
    for m in migrations:
        print(f"{m['rev']} | {m.get('date','')} | {m.get('msg','')}")
    return migrations


def check_last_migration(migrations):
    print("\n== Verifica ultima migrazione ==")
    if not migrations:
        print("[ERRORE] Nessuna migrazione trovata!")
        sys.exit(1)
    last = migrations[0]  # history --verbose is in reverse order (latest first)
    # Accept merge heads if one of the merged revisions is add_outbox_pattern_fields or outbox_pattern_001
    if (
        'add_outbox_pattern_fields' in last['msg'] or
        'outbox_pattern' in last['rev'] or
        ('merge' in last['msg'].lower() and any(
            'add_outbox_pattern_fields' in m['msg'] or 'outbox_pattern' in m['rev']
            for m in migrations[:3]  # check top 3 for safety
        ))
    ):
        print(f"[OK] Ultima migrazione (o merge): {last['msg']} ({last['rev']})")
    else:
        print(f"[ERRORE] Ultima migrazione non e' 'add_outbox_pattern_fields': {last['msg']} ({last['rev']})")
        sys.exit(1)


def check_indices():
    import asyncio

    import sqlalchemy as sa

    from src.shared.infra.database import engine
    print("\n== Verifica indici ==")

    async def async_check():
        async with engine.connect() as conn:
            def sync_check_indices(sync_conn):
                insp = sa.inspect(sync_conn)
                indices = insp.get_indexes('estimate_events')
                found_ix1 = any(ix['name'] == 'ix_estimate_events_unprocessed' for ix in indices)
                found_ix2 = any(ix['name'] == 'ix_estimate_event_timeline' for ix in indices)
                if found_ix1:
                    print("[OK] Indice ix_estimate_events_unprocessed presente")
                else:
                    print("[ERRORE] Indice ix_estimate_events_unprocessed mancante")
                if found_ix2:
                    print("[OK] Indice ix_estimate_event_timeline presente")
                else:
                    print("[ERRORE] Indice ix_estimate_event_timeline mancante")
                if not (found_ix1 and found_ix2):
                    sys.exit(1)
            await conn.run_sync(sync_check_indices)
    asyncio.run(async_check())


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-head-check', action='store_true', help='Salta il controllo sulla migration più recente')
    args = parser.parse_args()

    get_current_revision()
    migrations = list_all_migrations()
    if not args.skip_head_check:
        check_last_migration(migrations)
    check_indices()
    print("\n== Verifica migrazioni Alembic completata ==")

if __name__ == "__main__":
    main()
