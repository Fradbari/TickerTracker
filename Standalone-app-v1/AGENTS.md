# Piano Atomico TickerTracker v3.0

## Guida per LLM (Claude Code / Antigravity / Jules)

---

## Struttura dei file derivati
- backend.md: task backend/infra/drive (codice).
- frontend.md: task frontend/UX.
- docker.md: compose e packaging Docker.
- docs.md: testing, CI/CD e documentazione operativa/API.

> Le sezioni e i task originali sono stati riorganizzati per area, con meta‑header standard e istruzioni per LLM al termine di ciascun task.

---

# APPENDICE: Dipendenze tra Task

Priorità MVP (ambiente locale single‑user):

- Sezione 1: tutti i task 1.1-1.8.

- Sezione 2: 2.1-2.6, 2.10, 2.12-2.13, 2.16-2.21, 2.24-2.27.

- Sezione 3: solo 3.10 (facoltativo) e 3.12 (obbligatorio); il resto è Fase 2.

- Sezione 4: 4.1-4.10, 4.7; 4.11-4.12 subito dopo se vuoi completare UX.

- Sezione 5: almeno test unitari/lint (5.x base), E2E/CI/CD restano Fase 2.

```

Sezione 1 (Setup base):

1.1 → 1.2 → 1.3 → 1.4 → 1.5

1.6 (parallelo a 1.3-1.5)

1.8 (parallelo, richiede solo 1.1)

Sezione 2 (Backend):

2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6 → 2.10

2.7, 2.8, 2.9 (paralleli dopo 2.3)

2.11 (richiede 2.4, 2.6)

2.12 (richiede 2.4, 2.10)

2.13 (richiede 2.6, 2.10)

2.14 (richiede 2.12)

2.15 (richiede 2.5, 2.12)

2.16 (richiede 2.14)

2.17 → 2.18 → 2.19

2.20 → 2.21 → 2.22 → 2.23 (collegati 2.21, 2.22, 2.23)

2.24 (richiede 2.11, 2.22)

2.25 (richiede 2.24)

Sezione 3 (Sicurezza/Observability):

Tutti paralleli dopo completamento 2.20.

- 3.12: priorità alta (MVP locale).

- 3.10: priorità media (post-MVP).

- 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.11: Fase 2 (opzionali per uso single‑user).

Sezione 4 (Frontend):

4.1 → 4.2 → 4.3 → 4.4

4.5 → 4.6, 4.7, 4.8 , 4.9, 4.10, 4.11, 4.12

4.13 (richiede 4.6)

4.14 (richiede 4.6)

4.15 (richiede 4.5)

Sezione 5 (Testing/CI):

5.1 → 5.2, 5.3, 5.4, 5.5

5.6 → 5.7

5.8 (richiede 5.1, 5.6)

5.9 (richiede 5.4)

5.10 (richiede 5.4, 5.7)

5.11 (richiede 5.10)

5.12-5.17 (paralleli dopo setup base)

```

---

# NOTE PER L'LLM ESECUTORE

1\. **Esegui un task alla volta** e verifica gli acceptance criteria prima di procedere

2\. **Chiedi chiarimenti** se un requisito è ambiguo

3\. **Documenta** ogni scelta implementativa non ovvia

4\. **Testa** ogni componente prima di passare al successivo

5\. **Committa** con messaggi descrittivi che referenziano il task ID

6\. **Segnala** blocchi o dipendenze mancanti

---

# NOTE PER L'LLM ESECUTORE

1\. **Esegui un task alla volta** e verifica gli acceptance criteria prima di procedere

2\. **Chiedi chiarimenti** se un requisito è ambiguo

3\. **Documenta** ogni scelta implementativa non ovvia

4\. **Testa** ogni componente prima di passare al successivo

5\. **Committa** con messaggi descrittivi che referenziano il task ID

6\. **Segnala** blocchi o dipendenze mancanti
