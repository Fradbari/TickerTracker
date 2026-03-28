# End-to-End Testing (Playwright)

## Esecuzione dei Test
Assicurarsi che le dipendenze in \`frontend\` siano installate, e di avere Playwright pronto.

Dalla cartella radice (\`Standalone-app-v1\`), lanciare:
\`\`\`bash
npx playwright test
\`\`\`

## Struttura
- \`playwright.config.ts\`: Configurazione di base. Avvia sia backend (via \`uvicorn\`) che frontend (via \`npm run dev\`) se non già eseguiti.
- \`e2e/setup/global-setup.ts\`: Si occupa di invocare \`/api/test/seed\` al backend per garantire uno stato pulito (database vuoto e tabelle pronte).
- \`e2e/specs/\`: Contiene le suite di navigazione e validazione dei flussi principali.

## Flussi Implementati
- **Estimate Flow** (\`estimate-flow.spec.ts\`): Testa la creazione di una nuova stima compilando i campi principali.
- **Portfolio Flow** (\`portfolio-flow.spec.ts\`): Verifica l'apertura e visualizzazione della vista Portfolio.
- **Chat AI Flow** (\`chat-ai-flow.spec.ts\`): Invia un messaggio alla chat AI. Per test completi la API AI dovrebbe essere mockata se non si ha una key reale impostata nell'ambiente di test.

## Artifacts
Screenshots (soltanto per errori) e Video sono conservati in \`playwright-report/\` e generati in caso i test falliscano.

