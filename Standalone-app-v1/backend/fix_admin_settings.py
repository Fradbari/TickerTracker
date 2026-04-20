import re

with open(r'C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1\frontend\src\features\admin\components\AdminSettings.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

finnhub_component = '''
export const FinnhubSettings: React.FC = () => {
  const [apiKey, setApiKey] = useState('')
  const [visible, setVisible] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const [quota, setQuota] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/admin/config/finnhub-key', {
      headers: { 'Authorization': Bearer  }
    })
      .then(res => res.json())
      .then(data => {
        if (data.exists) {
           setApiKey('********')
        }
      })
      .catch(() => {})
  }, [])

  const handleValidate = async () => {
    setLoading(true)
    setStatus(null)
    setQuota(null)
    try {
      const res = await fetch('/api/admin/config/finnhub-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': Bearer 
        },
        body: JSON.stringify({ api_key: apiKey })
      })
      const data = await res.json()
      if (res.ok && data.valid) {
         setStatus('Valida')
         setQuota(data.quota_remaining)
      } else {
         setStatus('Non valida')
      }
    } catch (e) {
      setStatus('Errore connessione')
    }
    setLoading(false)
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow mt-8 p-6">
      <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-4">Integrazioni Esterne</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Finnhub API Key
          </label>
          <div className="flex items-center space-x-2">
            <input
              data-testid="finnhub-api-key"
              type={visible ? "text" : "password"}
              className="flex-1 p-2 border rounded dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Inserisci API Key Finnhub"
            />
            <button 
              type="button" 
              onClick={() => setVisible(!visible)}
              className="px-3 py-2 bg-gray-200 dark:bg-slate-600 rounded text-sm"
              data-testid="toggle-visibility"
            >
              {visible ? 'Nascondi' : 'Mostra'}
            </button>
          </div>
        </div>

        <button
          data-testid="validate-finnhub"
          onClick={handleValidate}
          disabled={loading || !apiKey}
          className="mt-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded"
        >
          {loading ? 'Verifica in corso...' : 'Valida e Salva'}
        </button>

        {status && (
          <div className={mt-2 text-sm }>
            Stato: {status}
            {quota &&  (Quota residua: /60)}
          </div>
        )}
      </div>
    </div>
  )
}
'''

new_text = text + finnhub_component

with open(r'C:\Users\francesco.dilecce\OneDrive - LUTECH SPA\Documenti\2. PERSONALI\3. Altro\Ticker Tracker\AI Studio\Standalone-app-v1\frontend\src\features\admin\components\AdminSettings.tsx', 'w', encoding='utf-8') as f:
    f.write(new_text)
