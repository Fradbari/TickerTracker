import re

path = r'C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1\frontend\src\features\admin\components\AdminDashboard.tsx'

with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "import { AdminSettings } from './AdminSettings'",
    "import { AdminSettings, FinnhubSettings } from './AdminSettings'"
)

text = text.replace(
    "<AdminSettings />",
    "<AdminSettings />\n      <FinnhubSettings />"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
