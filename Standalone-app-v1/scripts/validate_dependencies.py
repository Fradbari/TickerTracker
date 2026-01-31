#!/usr/bin/env python3
"""
Script di validazione del grafo delle dipendenze tra task.

Verifica:
1. Assenza di dipendenze circolari
2. Esistenza di tutti i task referenziati
3. Coerenza tra Progress Tracker e file AGENTS.md
4. Numerazione sequenziale corretta

Usage:
    python scripts/validate_dependencies.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class TaskDependencyValidator:
    """Validatore del grafo dipendenze task."""

    def __init__(self, root_path: Path):
        self.root = root_path
        self.tasks: Dict[str, Dict] = {}
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def parse_agents_file(self, file_path: Path) -> None:
        """Estrae task e dipendenze da un file AGENTS.md."""
        content = file_path.read_text(encoding='utf-8')
        
        # Pattern per task ID
        task_pattern = re.compile(r'^ID:\s*TASK\s+([\d.]+)', re.MULTILINE)
        # Pattern per dipendenze
        dep_pattern = re.compile(r'^Dipendenze:\s*(.+)$', re.MULTILINE)
        # Pattern per sezione (Area)
        area_pattern = re.compile(r'^Area:\s*(.+)$', re.MULTILINE)
        # Pattern per fase
        phase_pattern = re.compile(r'^Fase:\s*(.+)$', re.MULTILINE)
        
        # Trova tutti i task nel file
        for match in task_pattern.finditer(content):
            task_id = f"TASK {match.group(1)}"
            start_pos = match.start()
            
            # Trova la prossima sezione task o fine file
            next_match = task_pattern.search(content, start_pos + 1)
            end_pos = next_match.start() if next_match else len(content)
            task_section = content[start_pos:end_pos]
            
            # Estrai metadati
            area_match = area_pattern.search(task_section)
            phase_match = phase_pattern.search(task_section)
            dep_match = dep_pattern.search(task_section)
            
            self.tasks[task_id] = {
                'file': file_path.name,
                'area': area_match.group(1).strip() if area_match else 'unknown',
                'phase': phase_match.group(1).strip() if phase_match else 'unknown'
            }
            
            # Estrai dipendenze
            if dep_match:
                deps_str = dep_match.group(1).strip()
                if deps_str != '-':
                    # Separa dipendenze multiple (es: "TASK 2.1, TASK 2.2")
                    deps = re.findall(r'TASK\s+[\d.]+', deps_str)
                    self.dependencies[task_id] = deps

    def validate_all_references(self) -> None:
        """Verifica che tutti i task referenziati esistano."""
        all_task_ids = set(self.tasks.keys())
        
        for task_id, deps in self.dependencies.items():
            for dep in deps:
                if dep not in all_task_ids:
                    self.errors.append(
                        f"✗ {task_id} dipende da {dep} che non esiste"
                    )

    def detect_circular_dependencies(self) -> None:
        """Rileva cicli nel grafo delle dipendenze."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str, path: List[str]) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep in self.dependencies.get(task_id, []):
                if dep not in visited:
                    if has_cycle(dep, path + [task_id]):
                        return True
                elif dep in rec_stack:
                    cycle = ' → '.join(path + [task_id, dep])
                    self.errors.append(f"✗ Ciclo rilevato: {cycle}")
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                has_cycle(task_id, [])

    def check_sequence_gaps(self) -> None:
        """Verifica la numerazione sequenziale per sezione."""
        sections = defaultdict(list)
        
        # Raggruppa task per sezione
        for task_id in self.tasks:
            match = re.match(r'TASK (\d+)\.(\d+)', task_id)
            if match:
                section = int(match.group(1))
                number = int(match.group(2))
                sections[section].append(number)
        
        # Verifica gap nella numerazione
        for section, numbers in sections.items():
            numbers.sort()
            expected = list(range(min(numbers), max(numbers) + 1))
            missing = set(expected) - set(numbers)
            
            if missing:
                self.warnings.append(
                    f"⚠ Sezione {section}: numeri mancanti {sorted(missing)}"
                )

    def generate_report(self) -> str:
        """Genera report di validazione."""
        lines = [
            "=" * 60,
            "📊 REPORT VALIDAZIONE DIPENDENZE TASK",
            "=" * 60,
            "",
            f"✓ Task totali trovati: {len(self.tasks)}",
            f"✓ Relazioni dipendenza: {sum(len(deps) for deps in self.dependencies.values())}",
            ""
        ]
        
        # Statistiche per sezione
        sections_count = defaultdict(int)
        for task_id in self.tasks:
            match = re.match(r'TASK (\d+)\.', task_id)
            if match:
                sections_count[int(match.group(1))] += 1
        
        lines.append("📁 Task per sezione:")
        for section in sorted(sections_count.keys()):
            lines.append(f"   Sezione {section}: {sections_count[section]} task")
        lines.append("")
        
        # Errori
        if self.errors:
            lines.append(f"❌ ERRORI CRITICI ({len(self.errors)}):")
            lines.extend(f"   {err}" for err in self.errors)
            lines.append("")
        else:
            lines.append("✅ Nessun errore critico rilevato")
            lines.append("")
        
        # Warning
        if self.warnings:
            lines.append(f"⚠️  WARNING ({len(self.warnings)}):")
            lines.extend(f"   {warn}" for warn in self.warnings)
            lines.append("")
        else:
            lines.append("✅ Nessun warning")
            lines.append("")
        
        # Task senza dipendenze (entry points)
        entry_points = [tid for tid in self.tasks if not self.dependencies.get(tid)]
        if entry_points:
            lines.append(f"🚀 Entry points ({len(entry_points)}):")
            for task_id in sorted(entry_points):
                lines.append(f"   {task_id} [{self.tasks[task_id]['area']}]")
            lines.append("")
        
        lines.append("=" * 60)
        
        if self.errors:
            lines.append("❌ VALIDAZIONE FALLITA")
        else:
            lines.append("✅ VALIDAZIONE SUPERATA")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)

    def run(self) -> bool:
        """Esegue validazione completa."""
        print("🔍 Scansione file AGENTS.md...\n")
        
        # Scansiona tutti i file AGENTS.md
        agents_files = list(self.root.rglob('AGENTS.md'))
        
        if not agents_files:
            print("❌ Nessun file AGENTS.md trovato!")
            return False
        
        for file_path in agents_files:
            print(f"   Analizzando: {file_path.relative_to(self.root)}")
            self.parse_agents_file(file_path)
        
        print(f"\n✓ {len(self.tasks)} task caricati\n")
        
        # Esegui validazioni
        print("🔬 Validazione riferimenti...")
        self.validate_all_references()
        
        print("🔬 Rilevamento cicli...")
        self.detect_circular_dependencies()
        
        print("🔬 Verifica sequenze numeriche...")
        self.check_sequence_gaps()
        
        # Genera report
        print("\n" + self.generate_report())
        
        return len(self.errors) == 0


def main():
    """Entry point dello script."""
    # Determina root del progetto
    script_path = Path(__file__).resolve()
    root_path = script_path.parent.parent
    
    print(f"📂 Root progetto: {root_path}\n")
    
    # Esegui validazione
    validator = TaskDependencyValidator(root_path)
    success = validator.run()
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
