const fs = require('fs');
let content = fs.readFileSync('Standalone-app-v1/frontend/src/features/admin/components/AdminSettings.tsx', 'utf8');

if (!content.includes('import toast')) {
  content = "import toast from 'react-hot-toast'\n" + content;
}

content = content.replace(
  "    setSaved(true)\n  }",
  "    setSaved(true)\n    toast.success('Configurazione salvata')\n  }"
);

// We need regex to match properly or simpler replace
const expSrc = "await fetch('/api/sync/export', { method: 'POST' })";
const expTarget = \	oast.success('Backup avviato')
    try {
      const res = await fetch('/api/sync/export', { method: 'POST' })
      if (!res.ok) throw new Error('Export failed')
      toast.success('Backup completato')
    } catch (e: any) {
      toast.error(\\\Backup fallita: \. Riprova o controlla la console.\\\)
    }\;

content = content.replace(expSrc, expTarget);

const impSrc = "await fetch('/api/sync/import', { method: 'POST' })";
const impTarget = \	ry {
      const res = await fetch('/api/sync/import', { method: 'POST' })
      if (!res.ok) throw new Error('Import failed')
      toast.success('Ripristino completato')
    } catch (e: any) {
      toast.error(\\\Ripristino fallita: \. Riprova o controlla la console.\\\)
    }\;

content = content.replace(impSrc, impTarget);

fs.writeFileSync('Standalone-app-v1/frontend/src/features/admin/components/AdminSettings.tsx', content, 'utf8');
