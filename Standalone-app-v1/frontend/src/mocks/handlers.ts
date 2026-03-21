import { http, HttpResponse, delay } from 'msw';

export const handlers = [
  // Locale handler for i18next
  http.get('/locales/:lng/:ns.json', () => {
    return HttpResponse.json({});
  }),

  // Example handler
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'ok' });
  }),
  
  // Estimates handlers
  http.get('/api/estimates', () => {
    return HttpResponse.json([]);
  }),

  http.post('/api/estimates', async () => {
    // Optionally we leave this basic, tests can override it with their own delay or errors if they want
    return HttpResponse.json({ id: '123', ticker: 'AAPL', target_price: 150 }, { status: 201 });
  }),

  // Ticker search handler
  http.get('/api/tickers/search', ({ request }) => {
    const url = new URL(request.url);
    const q = url.searchParams.get('q') || '';
    
    if (q === 'AAPL') {
      return HttpResponse.json([
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'AAPL.MI', name: 'Apple Inc. (Milan)' }
      ]);
    }
    
    return HttpResponse.json([
      { symbol: 'MSFT', name: 'Microsoft' },
      { symbol: 'TSLA', name: 'Tesla' }
    ]);
  }),
];
