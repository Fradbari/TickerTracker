import re

with open(r'C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1\frontend\src\features\estimates\components\EstimateForm.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import_statement = "import { SymbolSearchInput } from '@/components/form/SymbolSearchInput'\n"
if "SymbolSearchInput" not in text:
    text = text.replace("import { isApiError } from '@/shared/api'", "import { isApiError } from '@/shared/api'\n" + import_statement)

# Using split to be completely safe from unicode dashes
parts1 = text.split("      {/* ")
for i, p in enumerate(parts1):
    if "Ticker" in p and "label" in p and "inputMode=" in p:
        lines = ("      {/* " + p).splitlines()
        
        # reconstruct this block with new component
        new_block = '''      {/* -- Ticker ------------------------------------------ */}
      <div>
        <label
          htmlFor="ticker"
          className="block text-sm font-medium text-slate-300 mb-1.5"
        >
          Ticker <span className="text-red-400">*</span>
        </label>
        <SymbolSearchInput
          value={watchedTicker}
          onChange={(val, isValid) => {
            setValue('ticker', val, { shouldValidate: true })
          }}
          error={errors.ticker?.message}
          disabled={isLoading}
        />
      </div>

'''
        parts1[i] = new_block.replace("      {/* ", "", 1) # remove the first marker since join will add it back

text = "      {/* ".join(parts1)

with open(r'C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1\frontend\src\features\estimates\components\EstimateForm.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
