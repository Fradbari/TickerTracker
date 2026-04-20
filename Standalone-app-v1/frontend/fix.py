import re
path = r'C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1\backend\src\market_data\finnhub_client.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'raise HTTPException\(status_code=504,[^\)]+\)', 'raise HTTPException(status_code=504, detail="Gateway Timeout from Finnhub")', text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
