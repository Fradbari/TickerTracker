import { request, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const baseURL = 'http://localhost:8000'; // backend URL
  const requestContext = await request.newContext({ baseURL });
  
  // Try to reach backend, sometimes it might be slow to start, but Playwright webServer ensures it's available.
  try {
    const response = await requestContext.post('/api/test/seed');
    if (!response.ok()) {
      console.warn('Failed to seed DB via /api/test/seed, status: ', response.status());
    } else {
      console.log('Database seeded successfully via /api/test/seed');
    }
  } catch (err) {
    console.error('Error during global setup seeding:', err);
  }
}

export default globalSetup;
