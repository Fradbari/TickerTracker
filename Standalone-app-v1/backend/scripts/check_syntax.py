import py_compile
import sys
from pathlib import Path


def check_syntax():
    """Verifica la sintassi di tutti i file Python nella cartella src."""
    root = Path(__file__).parent.parent
    src_path = root / "src"

    print(f"🔍 Verifica sintassi Python in: {src_path}")

    errors = 0
    for py_file in src_path.rglob("*.py"):
        try:
            # Riduci l'output verboso, mostra solo errori
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            print(f"❌ Errore di sintassi in {py_file}:\n{e}")
            errors += 1
        except Exception as e:
            print(f"❓ Errore inaspettato durante il controllo di {py_file}: {e}")
            errors += 1

    if errors > 0:
        print(f"\nTotal errors found: {errors}")
        sys.exit(1)
    else:
        print("\n✅ Tutti i file Python hanno una sintassi valida.")
        sys.exit(0)

if __name__ == "__main__":
    check_syntax()
